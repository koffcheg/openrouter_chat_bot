from types import SimpleNamespace

import pytest

from bot.handlers.admin.status import status_command
from bot.services.ai.model_registry import ModelRegistry
from bot.services.health.status_service import StatusService


class FakeMessage:
    def __init__(self):
        self.chat = SimpleNamespace(id=100)
        self.from_user = SimpleNamespace(id=42)
        self.bot = SimpleNamespace()
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


class FakeRepo:
    async def get_or_create(self, chat_id):
        return SimpleNamespace(chat_id=chat_id, is_paused=False, system_prompt='sys', current_model_slug='meta-llama/llama-3.3-70b-instruct:free', preferred_language='ru')


class FakeAuditRepo:
    async def count_for_chat(self, chat_id):
        return 3


SETTINGS = SimpleNamespace(owner_ids=[42], default_user_cooldown_seconds=20, max_input_chars=4000, sqlite_path='./data/bot.db')


@pytest.mark.asyncio
async def test_status_command_includes_model_observability_fields():
    message = FakeMessage()
    status_service = StatusService()
    status_service.begin_request(chat_id=100, command='ask', selected_model='meta-llama/llama-3.3-70b-instruct:free', fallback_chain=['meta-llama/llama-3.3-70b-instruct:free', 'openrouter/free'])
    status_service.record_attempt(chat_id=100, model_slug='meta-llama/llama-3.3-70b-instruct:free')
    status_service.record_provider_error(chat_id=100, error_text='rate limit')
    status_service.record_attempt(chat_id=100, model_slug='openrouter/free')
    status_service.record_success(chat_id=100, model_slug='openrouter/free', duration_ms=250)
    await status_command(message, SETTINGS, FakeRepo(), ModelRegistry.default(), status_service, FakeAuditRepo())
    text = message.answers[0]
    assert 'настроенная_модель: meta-llama/llama-3.3-70b-instruct:free' in text
    assert 'попытки_моделей: meta-llama/llama-3.3-70b-instruct:free, openrouter/free' in text
    assert 'последняя_модель_ответа: openrouter/free' in text
    assert 'fallback_использован: да' in text
    assert 'записей_аудита: 3' in text
