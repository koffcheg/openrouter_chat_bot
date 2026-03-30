from types import SimpleNamespace

import pytest

from bot.handlers.admin.models import models_command, setmodel_command
from bot.services.ai.model_registry import ModelRegistry


class FakeMessage:
    def __init__(self, text=''):
        self.text = text
        self.chat = SimpleNamespace(id=100)
        self.from_user = SimpleNamespace(id=42)
        self.bot = SimpleNamespace()
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


class FakeRepo:
    def __init__(self):
        self.current = 'nvidia/nemotron-3-super-120b-a12b:free'

    async def get_or_create(self, chat_id):
        return SimpleNamespace(chat_id=chat_id, is_paused=False, system_prompt='sys', current_model_slug=self.current)

    async def set_model(self, chat_id, model_slug):
        self.current = model_slug
        return SimpleNamespace(chat_id=chat_id, is_paused=False, system_prompt='sys', current_model_slug=self.current)


class FakeAuditRepo:
    def __init__(self):
        self.calls = []

    async def append(self, **kwargs):
        self.calls.append(kwargs)


SETTINGS = SimpleNamespace(owner_ids=[42])


@pytest.mark.asyncio
async def test_models_command_lists_available_models():
    message = FakeMessage('/models')
    repo = FakeRepo()
    await models_command(message, SETTINGS, repo, ModelRegistry.default())
    assert message.answers
    assert 'Available models:' in message.answers[0]
    assert 'openrouter/free' in message.answers[0]


@pytest.mark.asyncio
async def test_setmodel_command_updates_current_model_and_audits():
    message = FakeMessage('/setmodel openrouter/free')
    repo = FakeRepo()
    audit = FakeAuditRepo()
    await setmodel_command(message, SETTINGS, repo, ModelRegistry.default(), audit)
    assert repo.current == 'openrouter/free'
    assert message.answers == ['Current model set to openrouter/free']
    assert audit.calls[0]['action'] == 'setmodel'


@pytest.mark.asyncio
async def test_setmodel_command_rejects_unknown_slug():
    message = FakeMessage('/setmodel unknown/model')
    repo = FakeRepo()
    audit = FakeAuditRepo()
    await setmodel_command(message, SETTINGS, repo, ModelRegistry.default(), audit)
    assert repo.current == 'nvidia/nemotron-3-super-120b-a12b:free'
    assert message.answers == ['Unknown or disabled model slug. Use /models to see the allowed list.']
    assert audit.calls == []
