from types import SimpleNamespace

import pytest

from bot.services.telegram.reply_sender import send_html_chunks


class FakeMessage:
    def __init__(self):
        self.calls = []

    async def answer(self, text, **kwargs):
        self.calls.append((text, kwargs))


@pytest.mark.asyncio
async def test_send_html_chunks_sets_parse_mode_html():
    message = FakeMessage()
    await send_html_chunks(message, '<b>Hello</b>', 4096, reply_to_message_id=42)
    assert message.calls == [
        ('<b>Hello</b>', {'reply_to_message_id': 42, 'parse_mode': 'HTML'})
    ]
