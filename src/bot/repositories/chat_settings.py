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
    preferred_language: str = 'auto'
    response_style: str = 'pretty'


class ChatSettingsRepository(BaseRepository):
    async def _get_preferences(self, chat_id: int) -> tuple[str, str]:
        cursor = await self.db.execute(
            "SELECT preferred_language, response_style FROM chat_preferences WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row:
            return row['preferred_language'], row['response_style']
        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "INSERT INTO chat_preferences (chat_id, preferred_language, response_style, created_at, updated_at) VALUES (?, 'auto', 'pretty', ?, ?)",
            (chat_id, now, now),
        )
        await self.db.commit()
        return 'auto', 'pretty'

    async def get_or_create(self, chat_id: int) -> ChatSettingsRecord:
        cursor = await self.db.execute(
            "SELECT chat_id, is_paused, system_prompt, current_model_slug FROM chat_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if not row:
            now = datetime.now(timezone.utc).isoformat()
            await self.db.execute(
                "INSERT INTO chat_settings (chat_id, is_paused, system_prompt, current_model_slug, created_at, updated_at) VALUES (?, 0, ?, ?, ?, ?)",
                (chat_id, DEFAULT_SYSTEM_PROMPT, DEFAULT_CHAT_MODEL, now, now),
            )
            await self.db.commit()
            row = {
                'chat_id': chat_id,
                'is_paused': 0,
                'system_prompt': DEFAULT_SYSTEM_PROMPT,
                'current_model_slug': DEFAULT_CHAT_MODEL,
            }
        preferred_language, response_style = await self._get_preferences(chat_id)
        return ChatSettingsRecord(
            chat_id=row['chat_id'],
            is_paused=bool(row['is_paused']),
            system_prompt=row['system_prompt'] or DEFAULT_SYSTEM_PROMPT,
            current_model_slug=row['current_model_slug'],
            preferred_language=preferred_language,
            response_style=response_style,
        )

    async def set_paused(self, chat_id: int, paused: bool) -> ChatSettingsRecord:
        record = await self.get_or_create(chat_id)
        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "UPDATE chat_settings SET is_paused = ?, updated_at = ? WHERE chat_id = ?",
            (1 if paused else 0, now, chat_id),
        )
        await self.db.commit()
        record.is_paused = paused
        return record

    async def set_model(self, chat_id: int, model_slug: str) -> ChatSettingsRecord:
        record = await self.get_or_create(chat_id)
        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "UPDATE chat_settings SET current_model_slug = ?, updated_at = ? WHERE chat_id = ?",
            (model_slug, now, chat_id),
        )
        await self.db.commit()
        record.current_model_slug = model_slug
        return record

    async def set_language(self, chat_id: int, preferred_language: str) -> ChatSettingsRecord:
        record = await self.get_or_create(chat_id)
        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "INSERT INTO chat_preferences (chat_id, preferred_language, response_style, created_at, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(chat_id) DO UPDATE SET preferred_language = excluded.preferred_language, updated_at = excluded.updated_at",
            (chat_id, preferred_language, record.response_style, now, now),
        )
        await self.db.commit()
        record.preferred_language = preferred_language
        return record

    async def set_style(self, chat_id: int, response_style: str) -> ChatSettingsRecord:
        record = await self.get_or_create(chat_id)
        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "INSERT INTO chat_preferences (chat_id, preferred_language, response_style, created_at, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(chat_id) DO UPDATE SET response_style = excluded.response_style, updated_at = excluded.updated_at",
            (chat_id, record.preferred_language, response_style, now, now),
        )
        await self.db.commit()
        record.response_style = response_style
        return record
