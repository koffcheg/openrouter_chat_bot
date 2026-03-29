from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name="admin_control")


@router.message(Command("pause"))
async def pause_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    await chat_settings_repository.set_paused(message.chat.id, True)
    await message.answer("Bot responses are paused for this chat.")


@router.message(Command("resume"))
async def resume_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    await chat_settings_repository.set_paused(message.chat.id, False)
    await message.answer("Bot responses are enabled for this chat.")
