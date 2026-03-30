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


@router.message(Command("status"))
async def status_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, model_registry: ModelRegistry, status_service: StatusService, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    record = await chat_settings_repository.get_or_create(message.chat.id)
    runtime = status_service.snapshot(chat_id=message.chat.id)
    audit_count = await audit_log_repository.count_for_chat(message.chat.id)
    fallback_chain = ' -> '.join(model_registry.slug for model_registry in [])
    fallback_chain = ' -> '.join(entry.slug for entry in model_registry.list_enabled() if entry.fallback_rank is not None)
    lines = [
        'Status:',
        f"paused: {'yes' if record.is_paused else 'no'}",
        f"configured_model: {record.current_model_slug}",
        f"fallback_chain: {fallback_chain or '-'}",
        f"last_command: {runtime.last_command or '-'}",
        f"selected_model: {runtime.selected_model or '-'}",
        f"attempted_models: {', '.join(runtime.attempted_models) if runtime.attempted_models else '-'}",
        f"last_served_model: {runtime.last_served_model or '-'}",
        f"fallback_used: {'yes' if runtime.fallback_used else 'no'}",
        f"last_provider_error: {runtime.last_provider_error or '-'}",
        f"last_duration_ms: {runtime.last_duration_ms if runtime.last_duration_ms is not None else '-'}",
        f"total_requests_seen: {runtime.total_requests}",
        f"provider_failures_seen: {runtime.provider_failures}",
        f"audit_entries: {audit_count}",
        f"cooldown_seconds: {settings.default_user_cooldown_seconds}",
        f"max_input_chars: {settings.max_input_chars}",
        f"sqlite_path: {settings.sqlite_path}",
    ]
    await message.answer("\n".join(lines))
