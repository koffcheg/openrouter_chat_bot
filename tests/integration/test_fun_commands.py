from types import SimpleNamespace

import pytest

from bot.handlers.public.fun import fun_command


class FakeMessage:
    def __init__(self, text='', reply_to_message=None):
        self.text = text
        self.caption = None
        self.reply_to_message = reply_to_message
        self.chat = SimpleNamespace(id=123)
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


class FakeOrchestrator:
    async def fun(self, *, chat_id, text, context=''):
        return f'FUN::{text}::{context}'


class FakeBuilder:
    @staticmethod
    def message_text(message):
        return (message.text or '').strip()

    def build_ancestor_context(self, message):
        return 'CTX'


SETTINGS = SimpleNamespace(telegram_message_max_len=4096)


@pytest.mark.asyncio
async def test_fun_uses_command_text():
    message = FakeMessage('/fun make it funny')
    await fun_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['FUN::make it funny::']


@pytest.mark.asyncio
async def test_fun_uses_reply_text_when_command_text_missing():
    replied = FakeMessage('reply text')
    message = FakeMessage('/fun', reply_to_message=replied)
    await fun_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['FUN::reply text::CTX']
