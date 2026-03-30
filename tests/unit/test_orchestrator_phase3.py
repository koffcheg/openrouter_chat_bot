from dataclasses import dataclass

import pytest

from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


@dataclass
class SettingsRecord:
    system_prompt: str = 'base system'
    current_model_slug: str = 'nvidia/nemotron-3-super-120b-a12b:free'


class DummyRepo:
    async def get_or_create(self, chat_id: int):
        return SettingsRecord()


class DummyClient:
    def __init__(self):
        self.calls = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str):
        self.calls.append((prompt, system_prompt, model))
        return 'ok'


def make_orchestrator(client: DummyClient) -> AIOrchestrator:
    return AIOrchestrator(
        openrouter_client=client,
        chat_settings_repository=DummyRepo(),
        model_router=ModelRouter(ModelRegistry.default()),
        status_service=StatusService(),
        max_input_chars=1000,
    )


@pytest.mark.asyncio
async def test_truth_includes_claim_and_context():
    client = DummyClient()
    orchestrator = make_orchestrator(client)
    result = await orchestrator.truth(chat_id=1, claim_text='claim body', context='ctx')
    assert result == 'ok'
    prompt, system_prompt, model = client.calls[0]
    assert 'Claim:\nclaim body' in prompt
    assert 'Conversation context:\nctx' in prompt
    assert 'Current UTC date:' in system_prompt
    assert model == 'nvidia/nemotron-3-super-120b-a12b:free'


@pytest.mark.asyncio
async def test_summary_and_fun_build_prompts():
    client = DummyClient()
    orchestrator = make_orchestrator(client)
    await orchestrator.summarize(chat_id=1, target_text='long text', context='reply ctx')
    await orchestrator.fun(chat_id=1, text='make it funny', context='reply ctx')
    assert 'Summarize the following text clearly and briefly.' in client.calls[0][0]
    assert 'Relevant conversation context:\nreply ctx' in client.calls[0][0]
    assert 'Respond in a playful, witty tone' in client.calls[1][0]
    assert 'Conversation context:\nreply ctx' in client.calls[1][0]
