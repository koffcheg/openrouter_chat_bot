from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.ai.model_registry import ModelRegistry
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name='admin_models')


@router.message(Command('models'))
async def models_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry) -> None:
    if not await ensure_admin(message, settings):
        return
    current = await chat_settings_repository.get_or_create(message.chat.id)
    lines = ['Available models:']
    for entry in model_registry.list_enabled():
        suffix = []
        if entry.slug == current.current_model_slug:
            suffix.append('current')
        if entry.is_default:
            suffix.append('default')
        if entry.fallback_rank is not None:
            suffix.append(f'fallback {entry.fallback_rank}')
        extra = f" [{' | '.join(suffix)}]" if suffix else ''
        lines.append(f"- {entry.slug} — {entry.label}{extra}")
    await message.answer('\n'.join(lines))


@router.message(Command('setmodel'))
async def setmodel_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry) -> None:
    if not await ensure_admin(message, settings):
        return
    raw_text = message.text or ''
    _, _, slug = raw_text.partition(' ')
    slug = slug.strip()
    if not slug:
        await message.answer('Usage: /setmodel <model_slug>')
        return
    if not model_registry.is_enabled(slug):
        await message.answer('Unknown or disabled model slug. Use /models to see the allowed list.')
        return
    updated = await chat_settings_repository.set_model(message.chat.id, slug)
    await message.answer(f'Current model set to {updated.current_model_slug}')
