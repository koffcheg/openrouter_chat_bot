from types import SimpleNamespace

import pytest

from bot.handlers.public.fun import fun_command


class FakeBot:
    async def send_chat_action(self, **kwargs):
        return None


class FakeMessage:
    _next_message_id = 1

    def __init__(self, text='', reply_to_message=None):
        self.text = text
        self.caption = None
        self.reply_to_message = reply_to_message
        self.chat = SimpleNamespace(id=123)
        self.message_id = FakeMessage._next_message_id
        FakeMessage._next_message_id += 1
        self.bot = FakeBot()
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append(text)


class FakeOrchestrator:
    async def fun(self, *, chat_id, text, context='', language_hint=None):
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
    assert message.answers == ['<b>FUN::make it funny::</b>']


@pytest.mark.asyncio
async def test_fun_uses_reply_text_when_command_text_missing():
    replied = FakeMessage('reply text')
    message = FakeMessage('/fun', reply_to_message=replied)
    await fun_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['<b>FUN::reply text::CTX</b>']
