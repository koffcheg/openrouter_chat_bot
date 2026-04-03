from __future__ import annotations

from aiogram.types import Message

from bot.config.settings import Settings
from bot.i18n.messages import resolve_reply_language, text as i18n_text


async def is_admin_or_owner(message: Message, settings: Settings) -> bool:
    user_id = message.from_user.id if message.from_user else 0
    if user_id in settings.owner_ids:
        return True
    chat_member = await message.bot.get_chat_member(message.chat.id, user_id)
    return chat_member.status in {"administrator", "creator"}


async def ensure_admin(message: Message, settings: Settings, preferred_language: str | None = None) -> bool:
    if await is_admin_or_owner(message, settings):
        return True
    detected = getattr(message, 'text', None) or getattr(message, 'caption', None) or ''
    detected_lang = 'en' if detected and detected.isascii() else 'ru'
    lang = resolve_reply_language(preferred_language or 'auto', detected_lang)
    await message.answer(i18n_text('admin_only', lang))
    return False
