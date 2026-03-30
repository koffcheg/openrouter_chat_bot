from types import SimpleNamespace

import pytest

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
