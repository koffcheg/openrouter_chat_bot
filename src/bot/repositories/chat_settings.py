from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from bot.core.constants import DEFAULT_CHAT_MODEL, DEFAULT_SYSTEM_PROMPT
from bot.repositories.base import BaseRepository


@dataclass(slots=True)
class ChatSettingsRecord:
    chat_id: int
    is_paused: bool
    system_prompt: str
    current_model_slug: str


class ChatSettingsRepository(BaseRepository):
    async def get_or_create(self, chat_id: int) -> ChatSettingsRecord:
        row = await self.db.execute_fetchone(
            "SELECT chat_id, is_paused, system_prompt, current_model_slug FROM chat_settings WHERE chat_id = ?",
            (chat_id,),
        )
        if row:
            return ChatSettingsRecord(
                chat_id=row["chat_id"],
                is_paused=bool(row["is_paused"]),
                system_prompt=row["system_prompt"] or DEFAULT_SYSTEM_PROMPT,
                current_model_slug=row["current_model_slug"],
            )

        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            """
            INSERT INTO chat_settings (chat_id, is_paused, system_prompt, current_model_slug, created_at, updated_at)
            VALUES (?, 0, ?, ?, ?, ?)
            """,
            (chat_id, DEFAULT_SYSTEM_PROMPT, DEFAULT_CHAT_MODEL, now, now),
        )
        await self.db.commit()
        return ChatSettingsRecord(
            chat_id=chat_id,
            is_paused=False,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            current_model_slug=DEFAULT_CHAT_MODEL,
        )
