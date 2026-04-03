from types import SimpleNamespace

import pytest

from bot.core.exceptions import UserInputError
from bot.handlers.public.ask import ask_command


class FakeBot:
    async def send_chat_action(self, **kwargs):
        return None


class FakeMessage:
    def __init__(self, text=''):
        self.text = text
        self.chat = SimpleNamespace(id=100)
        self.from_user = SimpleNamespace(id=42)
        self.bot = FakeBot()
        self.message_id = 1
        self.reply_to_message = None
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


class FakeChatSettingsRepo:
    async def get_or_create(self, chat_id):
        return SimpleNamespace(preferred_language='ru', is_paused=False)


class FakeCooldownRepo:
    async def remaining_cooldown(self, **kwargs):
        return 0

    async def touch(self, **kwargs):
        return None


class FakeRequestStateRepo:
    async def acquire(self, **kwargs):
        return 'token'

    async def release(self, **kwargs):
        return None


class FakeReplyBuilder:
    def message_text(self, message):
        return ''


class FakeOrchestrator:
    async def ask(self, **kwargs):
        raise UserInputError('Please provide text for this command.')


SETTINGS = SimpleNamespace(default_user_cooldown_seconds=20, telegram_message_max_len=4096, max_input_chars=4000)


@pytest.mark.asyncio
async def test_ask_command_localizes_empty_input_error():
    message = FakeMessage('/ask')
    await ask_command(
        message,
        FakeOrchestrator(),
        FakeChatSettingsRepo(),
        FakeCooldownRepo(),
        FakeRequestStateRepo(),
        FakeReplyBuilder(),
        SETTINGS,
    )
    assert message.answers == ['Пожалуйста, добавьте текст к этой команде.']
