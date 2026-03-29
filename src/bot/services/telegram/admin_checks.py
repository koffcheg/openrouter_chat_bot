from __future__ import annotations

from aiogram.types import Message

from bot.config.settings import Settings


async def is_admin_or_owner(message: Message, settings: Settings) -> bool:
    user_id = message.from_user.id if message.from_user else 0
    if user_id in settings.owner_ids:
        return True
    chat_member = await message.bot.get_chat_member(message.chat.id, user_id)
    return chat_member.status in {"administrator", "creator"}


async def ensure_admin(message: Message, settings: Settings) -> bool:
    if await is_admin_or_owner(message, settings):
        return True
    await message.answer("Only chat admins can use this command.")
    return False
