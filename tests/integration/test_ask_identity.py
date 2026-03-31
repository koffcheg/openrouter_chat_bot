from types import SimpleNamespace

import pytest

from bot.handlers.public.ask import ask_command


class FakeMessage:
    def __init__(self, text=''):
        self.text = text
        self.chat = SimpleNamespace(id=100)
        self.from_user = SimpleNamespace(id=42)
        self.message_id = 501
        self.reply_to_message = None
        self.answers = []

    async def answer(self, text, reply_to_message_id=None):
        self.answers.append((text, reply_to_message_id))


class FakeChatSettingsRepo:
    async def get_or_create(self, chat_id):
        return SimpleNamespace(is_paused=False, preferred_language='auto')


class FakeCooldownRepo:
    async def remaining_cooldown(self, **kwargs):
        return 0

    async def touch(self, **kwargs):
        return None


class FakeRequestStateRepo:
    async def acquire(self, **kwargs):
        return 'rk'

    async def release(self, **kwargs):
        return None


class FakeReplyBuilder:
    @staticmethod
    def message_text(message):
        return (message.text or '').strip()


class FailIfCalledOrchestrator:
    async def ask(self, **kwargs):
        raise AssertionError('Model call should not happen for identity questions')


SETTINGS = SimpleNamespace(default_user_cooldown_seconds=20, telegram_message_max_len=4096)


@pytest.mark.asyncio
async def test_ask_identity_english_is_rule_based():
    message = FakeMessage('/ask who are you?')
    await ask_command(message, FailIfCalledOrchestrator(), FakeChatSettingsRepo(), FakeCooldownRepo(), FakeRequestStateRepo(), FakeReplyBuilder(), SETTINGS)
    assert message.answers == [('<b>CumxAI</b> is the assistant for this chat.', 501)]


@pytest.mark.asyncio
async def test_ask_identity_russian_is_rule_based():
    message = FakeMessage('/ask Привет, кто ты?')
    await ask_command(message, FailIfCalledOrchestrator(), FakeChatSettingsRepo(), FakeCooldownRepo(), FakeRequestStateRepo(), FakeReplyBuilder(), SETTINGS)
    assert message.answers == [('<b>CumxAI</b> — ассистент этого чата.', 501)]
