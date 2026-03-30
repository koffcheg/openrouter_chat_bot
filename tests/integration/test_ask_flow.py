import pytest

from bot.core.exceptions import UserInputError
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


class DummyChatSettingsRepository:
    async def get_or_create(self, chat_id: int):
        class Settings:
            system_prompt = 'System'
            current_model_slug = 'nvidia/nemotron-3-super-120b-a12b:free'
        return Settings()


class DummyOpenRouterClient:
    def __init__(self) -> None:
        self.calls = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str | None = None) -> str:
        self.calls.append((prompt, system_prompt, model))
        return 'answer'


def make_orchestrator(client: DummyOpenRouterClient, max_input_chars: int = 100) -> AIOrchestrator:
    return AIOrchestrator(
        openrouter_client=client,
        chat_settings_repository=DummyChatSettingsRepository(),
        model_router=ModelRouter(ModelRegistry.default()),
        status_service=StatusService(),
        max_input_chars=max_input_chars,
    )


@pytest.mark.asyncio
async def test_orchestrator_ask_happy_path() -> None:
    client = DummyOpenRouterClient()
    orchestrator = make_orchestrator(client)

    result = await orchestrator.ask(chat_id=123, text='Hello')
    assert result == 'answer'
    assert client.calls
    prompt, system_prompt, model = client.calls[0]
    assert prompt == 'Hello'
    assert 'Current UTC date:' in system_prompt
    assert model == 'nvidia/nemotron-3-super-120b-a12b:free'


@pytest.mark.asyncio
async def test_orchestrator_ask_rejects_empty_input() -> None:
    orchestrator = make_orchestrator(DummyOpenRouterClient())

    with pytest.raises(UserInputError):
        await orchestrator.ask(chat_id=123, text='   ')


@pytest.mark.asyncio
async def test_orchestrator_ask_rejects_too_long_input() -> None:
    orchestrator = make_orchestrator(DummyOpenRouterClient(), max_input_chars=5)

    with pytest.raises(UserInputError):
        await orchestrator.ask(chat_id=123, text='toolong')
