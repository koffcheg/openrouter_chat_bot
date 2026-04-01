from types import SimpleNamespace

import pytest

from bot.handlers.public.summary import summary_command


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
    async def summarize(self, *, chat_id, target_text, context='', language_hint=None):
        return f'SUM::{target_text}::{context}'


class FakeBuilder:
    @staticmethod
    def message_text(message):
        return (message.text or '').strip()

    def build_ancestor_context(self, message):
        return 'CTX'


SETTINGS = SimpleNamespace(telegram_message_max_len=4096)


@pytest.mark.asyncio
async def test_summary_uses_reply_text_when_present():
    replied = FakeMessage('some text')
    message = FakeMessage('/sum', reply_to_message=replied)
    await summary_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['Summary\nSUM::some text::CTX']


@pytest.mark.asyncio
async def test_summary_requires_reply_or_inline_text():
    message = FakeMessage('/sum')
    await summary_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['Reply to a message or provide text after /sum.']
