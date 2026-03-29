import pytest
from types import SimpleNamespace

from bot.config.settings import Settings
from bot.services.telegram.admin_checks import is_admin_or_owner


class FakeBot:
    def __init__(self, status: str) -> None:
        self.status = status

    async def get_chat_member(self, chat_id: int, user_id: int):
        return SimpleNamespace(status=self.status)


@pytest.mark.asyncio
async def test_owner_allowlist_bypasses_chat_admin_status() -> None:
    settings = Settings(BOT_TOKEN="token", OPENROUTER_API_KEY="key", OWNER_USER_IDS="42")
    message = SimpleNamespace(chat=SimpleNamespace(id=100), from_user=SimpleNamespace(id=42), bot=FakeBot("member"))
    assert await is_admin_or_owner(message, settings) is True


@pytest.mark.asyncio
async def test_chat_admin_is_allowed() -> None:
    settings = Settings(BOT_TOKEN="token", OPENROUTER_API_KEY="key")
    message = SimpleNamespace(chat=SimpleNamespace(id=100), from_user=SimpleNamespace(id=7), bot=FakeBot("administrator"))
    assert await is_admin_or_owner(message, settings) is True
