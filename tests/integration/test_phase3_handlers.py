from types import SimpleNamespace

import pytest

from bot.handlers.public.fun import fun_command
from bot.handlers.public.summary import summary_command
from bot.handlers.public.truth import truth_command


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
    async def truth(self, *, chat_id, claim_text, context=''):
        return f'TRUTH::{claim_text}::{context}'

    async def summarize(self, *, chat_id, target_text, context=''):
        return f'SUM::{target_text}::{context}'

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
async def test_truth_requires_reply():
    message = FakeMessage('/truth')
    await truth_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['Reply to a message to use /truth.']


@pytest.mark.asyncio
async def test_summary_uses_reply_text_when_present():
    replied = FakeMessage('some text')
    message = FakeMessage('/sum', reply_to_message=replied)
    await summary_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['SUM::some text::CTX']


@pytest.mark.asyncio
async def test_fun_uses_command_text():
    message = FakeMessage('/fun make it funny')
    await fun_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers == ['FUN::make it funny::']
