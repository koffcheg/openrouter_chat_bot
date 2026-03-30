from __future__ import annotations

import json
from datetime import datetime, timezone

from bot.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository):
    async def append(self, *, chat_id: int, actor_user_id: int, action: str, old_value=None, new_value=None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        old_value_json = json.dumps(old_value, ensure_ascii=False) if old_value is not None else None
        new_value_json = json.dumps(new_value, ensure_ascii=False) if new_value is not None else None
        await self.db.execute(
            "INSERT INTO admin_audit_log (chat_id, actor_user_id, action, old_value_json, new_value_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, actor_user_id, action, old_value_json, new_value_json, now),
        )
        await self.db.commit()

    async def count_for_chat(self, chat_id: int) -> int:
        cursor = await self.db.execute("SELECT COUNT(*) AS count_value FROM admin_audit_log WHERE chat_id = ?", (chat_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return int(row['count_value']) if row else 0
