from dataclasses import dataclass

import pytest

from bot.core.constants import DEFAULT_SYSTEM_PROMPT
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


@dataclass
class SettingsRecord:
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    current_model_slug: str = 'nvidia/nemotron-3-super-120b-a12b:free'


class DummyRepo:
    async def get_or_create(self, chat_id: int):
        return SettingsRecord()


class DummyClient:
    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or ['**I am a virtual assistant**\n\nПочемупрограммисты'])

    async def complete(self, *, prompt: str, system_prompt: str, model: str):
        self.calls.append((prompt, system_prompt, model))
        if self.responses:
            return self.responses.pop(0)
        return '**I am a virtual assistant**\n\nПочемупрограммисты'


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
    assert 'I am a virtual assistant' in result
    prompt, system_prompt, model = client.calls[0]
    assert 'Analyze the following claim using internal knowledge only.' in prompt
    assert 'Claim:\nclaim body' in prompt
    assert 'Conversation context:\nctx' in prompt
    assert 'Current UTC date:' in system_prompt
    assert 'Always identify yourself as CumxAI' in system_prompt
    assert 'If the language is mixed or unclear, prefer Russian.' in system_prompt
    assert 'Do not use Markdown syntax' in system_prompt
    assert 'general non-technical audience' in system_prompt
    assert 'Use exactly four sections with these headings and no others:' in system_prompt
    assert 'What would need live verification' in system_prompt
    assert model == 'nvidia/nemotron-3-super-120b-a12b:free'


@pytest.mark.asyncio
async def test_summary_and_fun_build_prompts_and_cleanup_output():
    client = DummyClient(['**I am a virtual assistant**\n\nПочемупрограммисты', '**I am a virtual assistant**\n\nПочемупрограммисты'])
    orchestrator = make_orchestrator(client)
    summary_result = await orchestrator.summarize(chat_id=1, target_text='long text', context='reply ctx')
    fun_result = await orchestrator.fun(chat_id=1, text='make it funny', context='reply ctx')
    assert 'Summarize the following text clearly and briefly.' in client.calls[0][0]
    assert 'Relevant conversation context:\nreply ctx' in client.calls[0][0]
    assert 'short, simple, broadly understandable humor' in client.calls[1][0]
    assert 'Avoid programmer-only jokes' in client.calls[1][0]
    assert '**' not in summary_result
    assert 'Почему программисты' in summary_result
    assert '**' not in fun_result


@pytest.mark.asyncio
async def test_orchestrator_repairs_broken_mixed_language_output_once():
    broken = 'У presently нет科学依据表明 love to purple связана со schizophrenia.'
    repaired = 'Немає наукових підстав вважати, що любов до фіолетового кольору пов’язана із шизофренією.'
    client = DummyClient([broken, repaired])
    orchestrator = make_orchestrator(client)
    result = await orchestrator.ask(chat_id=1, text='question', language_hint='uk')
    assert 'фіолетового' in result
    assert len(client.calls) == 2
    repair_prompt, repair_system_prompt, _ = client.calls[1]
    assert 'Rewrite the answer below in clean Ukrainian only.' in repair_prompt
    assert 'Reply in Ukrainian.' in repair_system_prompt
