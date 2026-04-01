from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.audit_log import AuditLogRepository
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.ai.model_registry import ModelRegistry
from bot.services.health.status_service import StatusService
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name="admin_status")


def _ui_lang(preferred_language: str) -> str:
    if preferred_language in {'ua', 'uk'}:
        return 'ua'
    if preferred_language == 'en':
        return 'en'
    return 'ru'


def _texts(lang: str) -> dict[str, str]:
    if lang == 'en':
        return {
            'title': 'Status:',
            'yes': 'yes',
            'no': 'no',
            'paused': 'paused',
            'configured_model': 'configured_model',
            'preferred_language': 'preferred_language',
            'response_style': 'response_style',
            'fallback_chain': 'fallback_chain',
            'last_command': 'last_command',
            'selected_model': 'selected_model',
            'attempted_models': 'attempted_models',
            'last_served_model': 'last_served_model',
            'fallback_used': 'fallback_used',
            'last_provider_error': 'last_provider_error',
            'last_duration_ms': 'last_duration_ms',
            'total_requests_seen': 'total_requests_seen',
            'provider_failures_seen': 'provider_failures_seen',
            'audit_entries': 'audit_entries',
            'cooldown_seconds': 'cooldown_seconds',
            'max_input_chars': 'max_input_chars',
            'sqlite_path': 'sqlite_path',
        }
    if lang == 'ua':
        return {
            'title': 'Статус:',
            'yes': 'так',
            'no': 'ні',
            'paused': 'пауза',
            'configured_model': 'налаштована_модель',
            'preferred_language': 'обрана_мова',
            'response_style': 'стиль_відповідей',
            'fallback_chain': 'ланцюг_fallback',
            'last_command': 'остання_команда',
            'selected_model': 'вибрана_модель',
            'attempted_models': 'спробовані_моделі',
            'last_served_model': 'остання_модель_відповіді',
            'fallback_used': 'fallback_використано',
            'last_provider_error': 'остання_помилка_провайдера',
            'last_duration_ms': 'остання_тривалість_ms',
            'total_requests_seen': 'усього_запитів',
            'provider_failures_seen': 'збої_провайдера',
            'audit_entries': 'записи_аудиту',
            'cooldown_seconds': 'кулдаун_секунд',
            'max_input_chars': 'макс_символів_вводу',
            'sqlite_path': 'шлях_sqlite',
        }
    return {
        'title': 'Статус:',
        'yes': 'да',
        'no': 'нет',
        'paused': 'пауза',
        'configured_model': 'настроенная_модель',
        'preferred_language': 'предпочтительный_язык',
        'response_style': 'стиль_ответов',
        'fallback_chain': 'цепочка_fallback',
        'last_command': 'последняя_команда',
        'selected_model': 'выбранная_модель',
        'attempted_models': 'попытки_моделей',
        'last_served_model': 'последняя_модель_ответа',
        'fallback_used': 'fallback_использован',
        'last_provider_error': 'последняя_ошибка_провайдера',
        'last_duration_ms': 'последняя_длительность_ms',
        'total_requests_seen': 'всего_запросов',
        'provider_failures_seen': 'сбоев_провайдера',
        'audit_entries': 'записей_аудита',
        'cooldown_seconds': 'кулдаун_секунд',
        'max_input_chars': 'макс_символов_ввода',
        'sqlite_path': 'путь_sqlite',
    }


@router.message(Command("status"))
async def status_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry, status_service: StatusService, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    record = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(record.preferred_language)
    texts = _texts(lang)
    runtime = status_service.snapshot(chat_id=message.chat.id)
    audit_count = await audit_log_repository.count_for_chat(message.chat.id)
    fallback_chain = ' -> '.join(entry.slug for entry in model_registry.list_enabled() if entry.fallback_rank is not None)
    lines = [
        texts['title'],
        f"{texts['paused']}: {texts['yes'] if record.is_paused else texts['no']}",
        f"{texts['configured_model']}: {record.current_model_slug}",
        f"{texts['preferred_language']}: {record.preferred_language}",
        f"{texts['response_style']}: {record.response_style}",
        f"{texts['fallback_chain']}: {fallback_chain or '-'}",
        f"{texts['last_command']}: {runtime.last_command or '-'}",
        f"{texts['selected_model']}: {runtime.selected_model or '-'}",
        f"{texts['attempted_models']}: {', '.join(runtime.attempted_models) if runtime.attempted_models else '-'}",
        f"{texts['last_served_model']}: {runtime.last_served_model or '-'}",
        f"{texts['fallback_used']}: {texts['yes'] if runtime.fallback_used else texts['no']}",
        f"{texts['last_provider_error']}: {runtime.last_provider_error or '-'}",
        f"{texts['last_duration_ms']}: {runtime.last_duration_ms if runtime.last_duration_ms is not None else '-'}",
        f"{texts['total_requests_seen']}: {runtime.total_requests}",
        f"{texts['provider_failures_seen']}: {runtime.provider_failures}",
        f"{texts['audit_entries']}: {audit_count}",
        f"{texts['cooldown_seconds']}: {settings.default_user_cooldown_seconds}",
        f"{texts['max_input_chars']}: {settings.max_input_chars}",
        f"{texts['sqlite_path']}: {settings.sqlite_path}",
    ]
    await message.answer("\n".join(lines))
