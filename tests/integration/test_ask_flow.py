import pytest

from bot.core.exceptions import UserInputError
from bot.services.ai.orchestrator import AIOrchestrator


class DummyChatSettingsRepository:
    async def get_or_create(self, chat_id: int):
        class Settings:
            system_prompt = "System"
            current_model_slug = "nvidia/nemotron-3-super-120b-a12b:free"
        return Settings()


class DummyOpenRouterClient:
    def __init__(self) -> None:
        self.calls = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str | None = None) -> str:
        self.calls.append((prompt, system_prompt, model))
        return "answer"


@pytest.mark.asyncio
async def test_orchestrator_ask_happy_path() -> None:
    client = DummyOpenRouterClient()
    orchestrator = AIOrchestrator(
        openrouter_client=client,
        chat_settings_repository=DummyChatSettingsRepository(),
        max_input_chars=100,
    )

    result = await orchestrator.ask(chat_id=123, text="Hello")
    assert result == "answer"
    assert client.calls == [("Hello", "System", "nvidia/nemotron-3-super-120b-a12b:free")]


@pytest.mark.asyncio
async def test_orchestrator_ask_rejects_empty_input() -> None:
    orchestrator = AIOrchestrator(
        openrouter_client=DummyOpenRouterClient(),
        chat_settings_repository=DummyChatSettingsRepository(),
        max_input_chars=100,
    )

    with pytest.raises(UserInputError):
        await orchestrator.ask(chat_id=123, text="   ")
