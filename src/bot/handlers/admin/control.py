from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.audit_log import AuditLogRepository
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name="admin_control")


@router.message(Command("pause"))
async def pause_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    updated = await chat_settings_repository.set_paused(message.chat.id, True)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='pause', old_value={'is_paused': previous.is_paused}, new_value={'is_paused': updated.is_paused})
    await message.answer("Bot responses are paused for this chat.")


@router.message(Command("resume"))
async def resume_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    updated = await chat_settings_repository.set_paused(message.chat.id, False)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='resume', old_value={'is_paused': previous.is_paused}, new_value={'is_paused': updated.is_paused})
    await message.answer("Bot responses are enabled for this chat.")


@router.message(Command("setlang"))
async def setlang_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    raw_text = message.text or ''
    _, _, value = raw_text.partition(' ')
    value = value.strip().lower()
    if value == 'ua':
        value = 'uk'
    if value not in {'auto', 'ru', 'uk', 'en'}:
        await message.answer('Usage: /setlang auto|ru|uk|ua|en')
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    updated = await chat_settings_repository.set_language(message.chat.id, value)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='setlang', old_value={'preferred_language': previous.preferred_language}, new_value={'preferred_language': updated.preferred_language})
    await message.answer(f'Preferred language set to {updated.preferred_language}')


@router.message(Command("setstyle"))
async def setstyle_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    raw_text = message.text or ''
    _, _, value = raw_text.partition(' ')
    value = value.strip().lower()
    if value not in {'pretty', 'concise', 'playful'}:
        await message.answer('Usage: /setstyle pretty|concise|playful')
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    updated = await chat_settings_repository.set_style(message.chat.id, value)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='setstyle', old_value={'response_style': previous.response_style}, new_value={'response_style': updated.response_style})
    await message.answer(f'Response style set to {updated.response_style}')
