from types import SimpleNamespace

import pytest

from bot.handlers.public.truth import truth_command


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
    async def truth(self, *, chat_id, claim_text, context='', language_hint=None):
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
