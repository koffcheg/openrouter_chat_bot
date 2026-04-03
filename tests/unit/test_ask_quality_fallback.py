from dataclasses import dataclass

import pytest

from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


@dataclass
class SettingsRecord:
    system_prompt: str = 'You are a helpful assistant.'
    current_model_slug: str = 'nvidia/nemotron-3-super-120b-a12b:free'
    preferred_language: str = 'uk'
    response_style: str = 'pretty'


class DummyRepo:
    async def get_or_create(self, chat_id: int):
        return SettingsRecord()


class DummyClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str):
        self.calls.append((prompt, system_prompt, model))
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_ask_uses_safe_fallback_when_repair_is_still_invalid():
    client = DummyClient([
        'Чим таке наука? observation Flight NATURAL',
        'Чим таке наука? observation Flight NATURAL',
    ])
    orchestrator = AIOrchestrator(
        openrouter_client=client,
        chat_settings_repository=DummyRepo(),
        model_router=ModelRouter(ModelRegistry.default()),
        status_service=StatusService(),
        max_input_chars=4000,
    )
    result = await orchestrator.ask(chat_id=1, text='що таке наука?', language_hint='uk')
    assert 'Я не зміг сформувати надійну відповідь' in result
