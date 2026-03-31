from types import SimpleNamespace

import pytest

from bot.handlers.public.summary import summary_command
from bot.handlers.public.truth import truth_command


class FakeMessage:
    def __init__(self, text='', reply_to_message=None, message_id=10):
        self.text = text
        self.caption = None
        self.reply_to_message = reply_to_message
        self.chat = SimpleNamespace(id=123)
        self.message_id = message_id
        self.answers = []

    async def answer(self, text, reply_to_message_id=None):
        self.answers.append((text, reply_to_message_id))


class FakeOrchestrator:
    async def truth(self, **kwargs):
        return 'Assessment:\n- first'

    async def summarize(self, **kwargs):
        return 'Short summary:\n- one'


class FakeBuilder:
    @staticmethod
    def message_text(message):
        return (message.text or '').strip()

    def build_ancestor_context(self, message):
        return 'CTX'


SETTINGS = SimpleNamespace(telegram_message_max_len=4096)


@pytest.mark.asyncio
async def test_truth_replies_to_target_message():
    replied = FakeMessage('claim text', message_id=77)
    message = FakeMessage('/truth', reply_to_message=replied, message_id=88)
    await truth_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers[0][1] == 77


@pytest.mark.asyncio
async def test_summary_replies_to_target_message():
    replied = FakeMessage('summary me', message_id=55)
    message = FakeMessage('/sum', reply_to_message=replied, message_id=66)
    await summary_command(message, FakeOrchestrator(), FakeBuilder(), SETTINGS)
    assert message.answers[0][1] == 55
