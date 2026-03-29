from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name="admin_status")


@router.message(Command("status"))
async def status_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    record = await chat_settings_repository.get_or_create(message.chat.id)
    lines = [
        "Status:",
        f"paused: {'yes' if record.is_paused else 'no'}",
        f"model: {record.current_model_slug}",
        f"cooldown_seconds: {settings.default_user_cooldown_seconds}",
        f"max_input_chars: {settings.max_input_chars}",
    ]
    await message.answer("\n".join(lines))
