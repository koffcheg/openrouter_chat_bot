from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter

from bot.clients.openrouter import OpenRouterClient
from bot.core.exceptions import ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError, UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService

logger = logging.getLogger(__name__)


class AIOrchestrator:
    def __init__(self, *, openrouter_client: OpenRouterClient, chat_settings_repository: ChatSettingsRepository, model_router: ModelRouter, status_service: StatusService, max_input_chars: int) -> None:
        self.openrouter_client = openrouter_client
        self.chat_settings_repository = chat_settings_repository
        self.model_router = model_router
        self.status_service = status_service
        self.max_input_chars = max_input_chars

    def _system_prompt(self, base_prompt: str) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        return (
            f"{base_prompt}\n\n"
            f"Current UTC date: {today}.\n"
            "Do not claim to have live internet access or real-time data unless it is provided in the prompt."
        )

    async def _complete(self, *, chat_id: int, user_prompt: str, command: str) -> str:
        cleaned = user_prompt.strip()
        if not cleaned:
            raise UserInputError('Please provide text for this command.')
        if len(cleaned) > self.max_input_chars:
            raise UserInputError(f'Input is too long. Maximum length is {self.max_input_chars} characters.')
        chat_settings = await self.chat_settings_repository.get_or_create(chat_id)
        model_sequence = self.model_router.model_sequence(chat_settings.current_model_slug)
        self.status_service.begin_request(
            chat_id=chat_id,
            command=command,
            selected_model=chat_settings.current_model_slug,
            fallback_chain=model_sequence,
        )
        started = perf_counter()
        last_exc = None
        for model_slug in model_sequence:
            self.status_service.record_attempt(chat_id=chat_id, model_slug=model_slug)
            try:
                result = await self.openrouter_client.complete(
                    prompt=cleaned,
                    system_prompt=self._system_prompt(chat_settings.system_prompt),
                    model=model_slug,
                )
                duration_ms = int((perf_counter() - started) * 1000)
                self.status_service.record_success(chat_id=chat_id, model_slug=model_slug, duration_ms=duration_ms)
                logger.info('AI request succeeded command=%s selected_model=%s served_model=%s attempted_models=%s fallback_used=%s duration_ms=%s', command, chat_settings.current_model_slug, model_slug, self.status_service.snapshot(chat_id=chat_id).attempted_models, self.status_service.snapshot(chat_id=chat_id).fallback_used, duration_ms)
                return result
            except (ProviderTimeoutError, ProviderRateLimitError, ProviderUnavailableError) as exc:
                last_exc = exc
                self.status_service.record_provider_error(chat_id=chat_id, error_text=str(exc))
                logger.warning('AI request transient failure command=%s selected_model=%s attempted_model=%s error=%s', command, chat_settings.current_model_slug, model_slug, exc)
                continue
        duration_ms = int((perf_counter() - started) * 1000)
        if last_exc is not None:
            self.status_service.record_terminal_failure(chat_id=chat_id, error_text=str(last_exc), duration_ms=duration_ms)
            raise last_exc
        raise RuntimeError('No model candidates available')

    async def ask(self, *, chat_id: int, text: str) -> str:
        return await self._complete(chat_id=chat_id, user_prompt=text, command='ask')

    async def truth(self, *, chat_id: int, claim_text: str, context: str = '') -> str:
        prompt = (
            'Analyze the following claim using internal knowledge only. '
            'Do not present the answer as live verification. '
            'Structure the answer with four sections: Assessment, Known facts, Uncertainty, What would need live verification.\n\n'
            f'Claim:\n{claim_text.strip()}'
        )
        if context.strip():
            prompt += f'\n\nConversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='truth')

    async def summarize(self, *, chat_id: int, target_text: str, context: str = '') -> str:
        prompt = f'Summarize the following text clearly and briefly.\n\nText:\n{target_text.strip()}'
        if context.strip():
            prompt += f'\n\nRelevant conversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='sum')

    async def fun(self, *, chat_id: int, text: str, context: str = '') -> str:
        prompt = f'Respond in a playful, witty tone while staying safe and coherent.\n\nUser request:\n{text.strip()}'
        if context.strip():
            prompt += f'\n\nConversation context:\n{context.strip()}'
        return await self._complete(chat_id=chat_id, user_prompt=prompt, command='fun')
