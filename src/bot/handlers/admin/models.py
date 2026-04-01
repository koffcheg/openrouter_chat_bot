from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.audit_log import AuditLogRepository
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.ai.model_registry import ModelRegistry
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name='admin_models')


def _ui_lang(preferred_language: str) -> str:
    if preferred_language in {'ua', 'uk'}:
        return 'ua'
    if preferred_language == 'en':
        return 'en'
    return 'ru'


def _texts(lang: str) -> dict[str, str]:
    if lang == 'en':
        return {
            'title': 'Available models:',
            'current': 'current',
            'default': 'default',
            'fallback': 'fallback',
            'usage': 'Usage: /setmodel <model_slug>',
            'unknown': 'Unknown or disabled model slug. Use /models to see the allowed list.',
            'set': 'Current model set to {value}',
        }
    if lang == 'ua':
        return {
            'title': 'Доступні моделі:',
            'current': 'поточна',
            'default': 'типова',
            'fallback': 'fallback',
            'usage': 'Використання: /setmodel <model_slug>',
            'unknown': 'Невідома або вимкнена модель. Використайте /models, щоб побачити дозволений список.',
            'set': 'Поточну модель встановлено: {value}',
        }
    return {
        'title': 'Доступные модели:',
        'current': 'текущая',
        'default': 'по умолчанию',
        'fallback': 'fallback',
        'usage': 'Использование: /setmodel <model_slug>',
        'unknown': 'Неизвестная или отключённая модель. Используйте /models, чтобы увидеть допустимый список.',
        'set': 'Текущая модель установлена: {value}',
    }


@router.message(Command('models'))
async def models_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry) -> None:
    if not await ensure_admin(message, settings):
        return
    current = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(current.preferred_language)
    texts = _texts(lang)
    lines = [texts['title']]
    for entry in model_registry.list_enabled():
        suffix = []
        if entry.slug == current.current_model_slug:
            suffix.append(texts['current'])
        if entry.is_default:
            suffix.append(texts['default'])
        if entry.fallback_rank is not None:
            suffix.append(f"{texts['fallback']} {entry.fallback_rank}")
        extra = f" [{' | '.join(suffix)}]" if suffix else ''
        lines.append(f"- {entry.slug} — {entry.label}{extra}")
    await message.answer('\n'.join(lines))


@router.message(Command('setmodel'))
async def setmodel_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    current = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(current.preferred_language)
    texts = _texts(lang)
    raw_text = message.text or ''
    _, _, slug = raw_text.partition(' ')
    slug = slug.strip()
    if not slug:
        await message.answer(texts['usage'])
        return
    if not model_registry.is_enabled(slug):
        await message.answer(texts['unknown'])
        return
    previous = current
    updated = await chat_settings_repository.set_model(message.chat.id, slug)
    await audit_log_repository.append(
        chat_id=message.chat.id,
        actor_user_id=message.from_user.id if message.from_user else 0,
        action='setmodel',
        old_value={'current_model_slug': previous.current_model_slug},
        new_value={'current_model_slug': updated.current_model_slug},
    )
    await message.answer(texts['set'].format(value=updated.current_model_slug))
