from __future__ import annotations

from time import time

from bot.repositories.base import BaseRepository


class CooldownStateRepository(BaseRepository):
    async def remaining_cooldown(self, *, chat_id: int, user_id: int, cooldown_seconds: int) -> int:
        cursor = await self.db.execute(
            "SELECT last_request_at FROM cooldown_state WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if not row:
            return 0
        remaining = cooldown_seconds - int(time() - float(row["last_request_at"]))
        return max(0, remaining)

    async def touch(self, *, chat_id: int, user_id: int) -> None:
        now = time()
        await self.db.execute(
            "INSERT INTO cooldown_state (chat_id, user_id, last_request_at) VALUES (?, ?, ?) ON CONFLICT(chat_id, user_id) DO UPDATE SET last_request_at = excluded.last_request_at",
            (chat_id, user_id, now),
        )
        await self.db.commit()
