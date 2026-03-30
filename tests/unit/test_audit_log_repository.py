import pytest

from bot.db.sqlite import connect, initialize_database
from bot.repositories.audit_log import AuditLogRepository


@pytest.mark.asyncio
async def test_audit_log_repository_appends_and_counts(tmp_path):
    db = await connect(str(tmp_path / 'bot.db'), 5000)
    await initialize_database(db)
    repo = AuditLogRepository(db)
    await repo.append(chat_id=100, actor_user_id=42, action='setmodel', old_value={'model': 'a'}, new_value={'model': 'b'})
    assert await repo.count_for_chat(100) == 1
    await db.close()
