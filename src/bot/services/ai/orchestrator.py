from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter

from bot.clients.openrouter import OpenRouterClient
from bot.core.exceptions import ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError, UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.ai.output_validator import build_repair_prompt, validate_output
from bot.services.ai.prompt_policies import command_policy_text, normalize_language_code, normalize_truth_sections
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService
from bot.utils.text import cleanup_model_text, detect_response_language

logger = logging.getLogger(__name__)


class AIOrchestrator:
    def __init__(self, *, openrouter_client: OpenRouterClient, chat_settings_repository: ChatSettingsRepository, model_router: ModelRouter, status_service: StatusService, max_input_chars: int) -> None:
        self.openrouter_client = openrouter_client
        self.chat_settings_repository = chat_settings_repository
        self.model_router = model_router
        self.status_service = status_service
        self.max_input_chars = max_input_chars

    def _system_prompt(self, *, base_prompt: str, language: str, style: str, command: str) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        style_text = {
            'pretty': 'Use short paragraphs, simple bullets when helpful, and readable section labels.',
            'concise': 'Be brief and direct. Prefer compact answers.',
            'playful': 'Use a light, friendly tone while staying clear and safe.',
        }.get(style, 'Use short paragraphs and readable structure.')
        normalized_language = normalize_language_code(language)
        language_text = {
            'ru': 'Reply in Russian.',
            'uk': 'Reply in Ukrainian.',
            'en': 'Reply in English.',
            'auto': f"Reply in {normalized_language}.",
        }.get(normalized_language, f"Reply in {normalized_language}.")
        command_text = command_policy_text(command, normalized_language)
        return (
            f"{base_prompt}\n\n"
            f"Current UTC date: {today}.\n"
            f"{language_text}\n"
            f"{style_text}\n"
            f"{command_text}\n"
            "Do not claim to have live internet access or real-time data unless it is provided in the prompt."
        )

    def _post_process_result(self, *, text: str, command: str, language: str) -> str:
        result = cleanup_model_text(text)
        if command == 'truth':
            result = normalize_truth_sections(result, language)
        return result

    async def _repair_once(self, *, text: str, system_prompt: str, model_slug: str, command: str, language: str) -> str:
        repaired = await self.openrouter_client.complete(
            prompt=build_repair_prompt(text=text, language=language, command=command),
            system_prompt=system_prompt,
            model=model_slug,
        )
        return self._post_process_result(text=repaired, command=command, language=language)

    async def _complete(self, *, chat_id: int, user_prompt: str, command: str, language_hint: str | None = None) -> str:
        cleaned = user_prompt.strip()
        if not cleaned:
            raise UserInputError('Please provide text for this command.')
        if len(cleaned) > self.max_input_chars:
            raise UserInputError(f'Input is too long. Maximum length is {self.max_input_chars} characters.')

        chat_settings = await self.chat_settings_repository.get_or_create(chat_id)
        preferred_language = normalize_language_code(getattr(chat_settings, 'preferred_language', 'auto'), fallback='auto')
        response_style = getattr(chat_settings, 'response_style', 'pretty')
        current_model_slug = getattr(chat_settings, 'current_model_slug', None)
        base_system_prompt = getattr(chat_settings, 'system_prompt', 'You are a helpful assistant.')

        detected_language = normalize_language_code(language_hint or detect_response_language(cleaned, 'ru'))
        target_language = detected_language if preferred_language == 'auto' else preferred_language
        model_sequence = self.model_router.model_sequence(current_model_slug)
        self.status_service.begin_request(chat_id=chat_id, command=command, selected_model=current_model_slug, fallback_chain=model_sequence)
        started = perf_counter()
        last_exc = None
        for model_slug in model_sequence:
            self.status_service.record_attempt(chat_id=chat_id, model_slug=model_slug)
            try:
                system_prompt = self._system_prompt(base_prompt=base_system_prompt, language=target_language, style=response_style, command=command)
                result = await self.openrouter_client.complete(
                    prompt=cleaned,
                    system_prompt=system_prompt,
                    model=model_slug,
                )
                result = self._post_process_result(text=result, command=command, language=target_language)
                validation = validate_output(text=result, language=target_language, command=command)
                if not validation.is_valid:
                    logger.warning('AI output validation failed command=%s model=%s reason=%s; attempting repair', command, model_slug, validation.reason)
                    repaired = await self._repair_once(text=result, system_prompt=system_prompt, model_slug=model_slug, command=command, language=target_language)
                    repaired_validation = validate_output(text=repaired, language=target_language, command=command)
                    if repaired_validation.is_valid or repaired.strip():
                        result = repaired
                duration_ms = int((perf_counter() - started) * 1000)
                self.status_service.record_success(chat_id=chat_id, model_slug=model_slug, duration_ms=duration_ms)
                logger.info('AI request succeeded command=%s selected_model=%s served_model=%s attempted_models=%s fallback_used=%s duration_ms=%s', command, current_model_slug, model_slug, self.status_service.snapshot(chat_id=chat_id).attempted_models, self.status_service.snapshot(chat_id=chat_id).fallback_used, duration_ms)
                return result
            except (ProviderTimeoutError, ProviderRateLimitError, ProviderUnavailableError) as exc:
                last_exc = exc
                self.status_service.record_provider_error(chat_id=chat_id, error_text=str(exc))
                logger.warning('AI request transient failure command=%s selected_model=%s attempted_model=%s error=%s', command, current_model_slug, model_slug, exc)
                continue
        duration_ms = int((perf_counter() - started) * 1000)
        if last_exc is not None:
            self.status_service.record_terminal_failure(chat_id=chat_id, error_text=str(last_exc), duration_ms=duration_ms)
            raise last_exc
        raise RuntimeError('No model candidates available')

    async def ask(self, *, chat_id: int, text: str, reply_context: str = '', language_hint: str | None = None) -> str:
        prompt = text.strip()
        if reply_context.strip():
            prompt = f"User request:\n{text.strip()}\n\nReplied message context:\n{reply_context.strip()}"
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='ask', language_hint=language_hint)

    async def truth(self, *, chat_id: int, claim_text: str, context: str = '', language_hint: str | None = None) -> str:
        prompt = (
            'Analyze the following claim using internal knowledge only. '
            'Do not present the answer as live verification.\n\n'
            f'Claim:\n{claim_text.strip()}'
        )
        if context.strip():
            prompt += f'\n\nConversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='truth', language_hint=language_hint)

    async def summarize(self, *, chat_id: int, target_text: str, context: str = '', language_hint: str | None = None) -> str:
        prompt = f'Summarize the following text clearly and briefly.\n\nText:\n{target_text.strip()}'
        if context.strip():
            prompt += f'\n\nRelevant conversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='sum', language_hint=language_hint)

    async def fun(self, *, chat_id: int, text: str, context: str = '', language_hint: str | None = None) -> str:
        prompt = (
            'Reply with short, simple, broadly understandable humor for a general audience. '
            'Avoid programmer-only jokes, niche technical references, and long explanations unless the user asks for them.\n\n'
            f'User request:\n{text.strip()}'
        )
        if context.strip():
            prompt += f'\n\nConversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='fun', language_hint=language_hint)
