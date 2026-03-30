import pytest

from bot.core.exceptions import ProviderRateLimitError
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


class DummyRepo:
    async def get_or_create(self, chat_id: int):
        class Settings:
            system_prompt = 'system'
            current_model_slug = 'nvidia/nemotron-3-super-120b-a12b:free'
        return Settings()


class FallbackClient:
    def __init__(self):
        self.models = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str):
        self.models.append(model)
        if len(self.models) == 1:
            raise ProviderRateLimitError('rate limit')
        return 'fallback-ok'


def test_model_router_builds_fallback_sequence():
    router = ModelRouter(ModelRegistry.default())
    sequence = router.model_sequence('nvidia/nemotron-3-super-120b-a12b:free')
    assert sequence[0] == 'nvidia/nemotron-3-super-120b-a12b:free'
    assert 'openrouter/free' in sequence


@pytest.mark.asyncio
async def test_orchestrator_uses_fallback_on_transient_error():
    client = FallbackClient()
    status_service = StatusService()
    orchestrator = AIOrchestrator(
        openrouter_client=client,
        chat_settings_repository=DummyRepo(),
        model_router=ModelRouter(ModelRegistry.default()),
        status_service=status_service,
        max_input_chars=1000,
    )
    result = await orchestrator.ask(chat_id=1, text='hello')
    assert result == 'fallback-ok'
    assert client.models[0] == 'nvidia/nemotron-3-super-120b-a12b:free'
    assert client.models[1] == 'openrouter/free'
    snapshot = status_service.snapshot(chat_id=1)
    assert snapshot.last_served_model == 'openrouter/free'
    assert snapshot.fallback_used is True
