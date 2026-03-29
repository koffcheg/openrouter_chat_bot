import pytest

from bot.db.sqlite import connect, initialize_database
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository


@pytest.mark.asyncio
async def test_request_lock_allows_only_one_active_request(tmp_path) -> None:
    db = await connect(str(tmp_path / "bot.db"), 5000)
    await initialize_database(db)
    repo = RequestStateRepository(db)
    first = await repo.acquire(chat_id=1, user_id=2)
    second = await repo.acquire(chat_id=1, user_id=2)
    assert first is not None
    assert second is None
    await repo.release(chat_id=1, user_id=2, request_key=first)
    third = await repo.acquire(chat_id=1, user_id=2)
    assert third is not None
    await db.close()


@pytest.mark.asyncio
async def test_cooldown_repository_reports_remaining_seconds(tmp_path) -> None:
    db = await connect(str(tmp_path / "bot.db"), 5000)
    await initialize_database(db)
    repo = CooldownStateRepository(db)
    assert await repo.remaining_cooldown(chat_id=1, user_id=2, cooldown_seconds=5) == 0
    await repo.touch(chat_id=1, user_id=2)
    remaining = await repo.remaining_cooldown(chat_id=1, user_id=2, cooldown_seconds=5)
    assert 0 < remaining <= 5
    await db.close()
