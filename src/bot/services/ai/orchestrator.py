from __future__ import annotations

from bot.clients.openrouter import OpenRouterClient
from bot.core.exceptions import UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository


class AIOrchestrator:
    def __init__(self, *, openrouter_client: OpenRouterClient, chat_settings_repository: ChatSettingsRepository, max_input_chars: int) -> None:
        self.openrouter_client = openrouter_client
        self.chat_settings_repository = chat_settings_repository
        self.max_input_chars = max_input_chars

    async def ask(self, *, chat_id: int, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            raise UserInputError("Please provide text after /ask.")
        if len(cleaned) > self.max_input_chars:
            raise UserInputError(f"Input is too long. Maximum length is {self.max_input_chars} characters.")
        chat_settings = await self.chat_settings_repository.get_or_create(chat_id)
        return await self.openrouter_client.complete(prompt=cleaned, system_prompt=chat_settings.system_prompt, model=chat_settings.current_model_slug)
