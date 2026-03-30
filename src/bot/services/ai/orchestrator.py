from __future__ import annotations

from datetime import datetime, timezone

from bot.clients.openrouter import OpenRouterClient
from bot.core.exceptions import UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository


class AIOrchestrator:
    def __init__(self, *, openrouter_client: OpenRouterClient, chat_settings_repository: ChatSettingsRepository, max_input_chars: int) -> None:
        self.openrouter_client = openrouter_client
        self.chat_settings_repository = chat_settings_repository
        self.max_input_chars = max_input_chars

    def _system_prompt(self, base_prompt: str) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        return (
            f"{base_prompt}\n\n"
            f"Current UTC date: {today}.\n"
            "Do not claim to have live internet access or real-time data unless it is provided in the prompt."
        )

    async def _complete(self, *, chat_id: int, user_prompt: str) -> str:
        cleaned = user_prompt.strip()
        if not cleaned:
            raise UserInputError("Please provide text for this command.")
        if len(cleaned) > self.max_input_chars:
            raise UserInputError(f"Input is too long. Maximum length is {self.max_input_chars} characters.")
        chat_settings = await self.chat_settings_repository.get_or_create(chat_id)
        return await self.openrouter_client.complete(
            prompt=cleaned,
            system_prompt=self._system_prompt(chat_settings.system_prompt),
            model=chat_settings.current_model_slug,
        )

    async def ask(self, *, chat_id: int, text: str) -> str:
        return await self._complete(chat_id=chat_id, user_prompt=text)

    async def truth(self, *, chat_id: int, claim_text: str, context: str = '') -> str:
        prompt = (
            "Analyze the following claim. Distinguish facts, assumptions, and uncertainty. "
            "Do not pretend to verify live information.\n\n"
            f"Claim:\n{claim_text.strip()}"
        )
        if context.strip():
            prompt += f"\n\nConversation context:\n{context.strip()}"
        return await self._complete(chat_id=chat_id, user_prompt=prompt)

    async def summarize(self, *, chat_id: int, target_text: str, context: str = '') -> str:
        prompt = f"Summarize the following text clearly and briefly.\n\nText:\n{target_text.strip()}"
        if context.strip():
            prompt += f"\n\nRelevant conversation context:\n{context.strip()}"
        return await self._complete(chat_id=chat_id, user_prompt=prompt)

    async def fun(self, *, chat_id: int, text: str, context: str = '') -> str:
        prompt = f"Respond in a playful, witty tone while staying safe and coherent.\n\nUser request:\n{text.strip()}"
        if context.strip():
            prompt += f"\n\nConversation context:\n{context.strip()}"
        return await self._complete(chat_id=chat_id, user_prompt=prompt)
