from __future__ import annotations

from time import time
from uuid import uuid4

from bot.repositories.base import BaseRepository


class RequestStateRepository(BaseRepository):
    async def acquire(self, *, chat_id: int, user_id: int) -> str | None:
        request_key = str(uuid4())
        try:
            await self.db.execute(
                "INSERT INTO active_requests (chat_id, user_id, started_at, request_key) VALUES (?, ?, ?, ?)",
                (chat_id, user_id, time(), request_key),
            )
            await self.db.commit()
            return request_key
        except Exception:
            return None

    async def release(self, *, chat_id: int, user_id: int, request_key: str) -> None:
        await self.db.execute(
            "DELETE FROM active_requests WHERE chat_id = ? AND user_id = ? AND request_key = ?",
            (chat_id, user_id, request_key),
        )
        await self.db.commit()
