from types import SimpleNamespace

import pytest

from bot.handlers.admin.control import setlang_command


class FakeMessage:
    def __init__(self, text=''):
        self.text = text
        self.chat = SimpleNamespace(id=100)
        self.from_user = SimpleNamespace(id=42)
        self.bot = SimpleNamespace()
        self.answers = []

    async def answer(self, text):
        self.answers.append(text)


class FakeRepo:
    def __init__(self, preferred_language='uk'):
        self.preferred_language = preferred_language

    async def get_or_create(self, chat_id):
        return SimpleNamespace(chat_id=chat_id, preferred_language=self.preferred_language)

    async def set_language(self, chat_id, value):
        self.preferred_language = value
        return SimpleNamespace(chat_id=chat_id, preferred_language=self.preferred_language)


class FakeAuditRepo:
    def __init__(self):
        self.calls = []

    async def append(self, **kwargs):
        self.calls.append(kwargs)


SETTINGS = SimpleNamespace(owner_ids=[42])


@pytest.mark.asyncio
async def test_setlang_replies_in_new_language_not_previous_one():
    message = FakeMessage('/setlang ru')
    repo = FakeRepo(preferred_language='uk')
    audit = FakeAuditRepo()
    await setlang_command(message, SETTINGS, repo, audit)
    assert message.answers == ['Язык ответов установлен: ru']
    assert audit.calls[0]['action'] == 'setlang'
