from dataclasses import dataclass

import pytest

from bot.services.ai.orchestrator import AIOrchestrator


@dataclass
class SettingsRecord:
    system_prompt: str = 'base system'
    current_model_slug: str = 'model-x'


class DummyRepo:
    async def get_or_create(self, chat_id: int):
        return SettingsRecord()


class DummyClient:
    def __init__(self):
        self.calls = []

    async def complete(self, *, prompt: str, system_prompt: str, model: str):
        self.calls.append((prompt, system_prompt, model))
        return 'ok'


@pytest.mark.asyncio
async def test_truth_includes_claim_and_context():
    client = DummyClient()
    orchestrator = AIOrchestrator(openrouter_client=client, chat_settings_repository=DummyRepo(), max_input_chars=1000)
    result = await orchestrator.truth(chat_id=1, claim_text='claim body', context='ctx')
    assert result == 'ok'
    prompt, system_prompt, model = client.calls[0]
    assert 'Claim:\nclaim body' in prompt
    assert 'Conversation context:\nctx' in prompt
    assert 'Current UTC date:' in system_prompt
    assert model == 'model-x'
