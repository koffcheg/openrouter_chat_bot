from __future__ import annotations

from dataclasses import dataclass

from aiogram import Dispatcher

from bot.clients.openrouter import OpenRouterClient
from bot.config.settings import Settings
from bot.db.sqlite import connect, initialize_database
from bot.handlers.admin.control import router as admin_control_router
from bot.handlers.admin.models import router as admin_models_router
from bot.handlers.admin.status import router as admin_status_router
from bot.handlers.public.ask import router as ask_router
from bot.handlers.public.fun import router as fun_router
from bot.handlers.public.help import router as help_router
from bot.handlers.public.summary import router as summary_router
from bot.handlers.public.truth import router as truth_router
from bot.middleware.errors import ErrorMiddleware
from bot.middleware.permissions import PermissionMiddleware
from bot.middleware.throttling import ThrottlingMiddleware
from bot.repositories.audit_log import AuditLogRepository
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService
from bot.services.telegram.context_builder import ReplyContextBuilder


@dataclass(slots=True)
class AppContainer:
    dispatcher: Dispatcher
    ai_orchestrator: AIOrchestrator
    db: object


async def build_application(settings: Settings) -> AppContainer:
    db = await connect(settings.sqlite_path, settings.sqlite_busy_timeout_ms)
    await initialize_database(db)

    chat_settings_repository = ChatSettingsRepository(db)
    cooldown_repository = CooldownStateRepository(db)
    request_state_repository = RequestStateRepository(db)
    audit_log_repository = AuditLogRepository(db)
    model_registry = ModelRegistry.default()
    model_router = ModelRouter(model_registry)
    status_service = StatusService()
    openrouter_client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        default_model=settings.openrouter_default_model,
        timeout_seconds=settings.request_timeout_seconds,
        http_referer=settings.openrouter_http_referer,
        app_title=settings.openrouter_app_title,
    )
    ai_orchestrator = AIOrchestrator(
        openrouter_client=openrouter_client,
        chat_settings_repository=chat_settings_repository,
        model_router=model_router,
        status_service=status_service,
        max_input_chars=settings.max_input_chars,
    )
    reply_context_builder = ReplyContextBuilder(
        max_messages=settings.max_context_messages,
        max_chars=settings.max_context_chars,
    )

    dispatcher = Dispatcher()
    dispatcher.update.middleware(ErrorMiddleware())
    dispatcher.update.middleware(PermissionMiddleware())
    dispatcher.update.middleware(ThrottlingMiddleware())
    dispatcher.include_router(help_router)
    dispatcher.include_router(ask_router)
    dispatcher.include_router(truth_router)
    dispatcher.include_router(summary_router)
    dispatcher.include_router(fun_router)
    dispatcher.include_router(admin_control_router)
    dispatcher.include_router(admin_status_router)
    dispatcher.include_router(admin_models_router)
    dispatcher['settings'] = settings
    dispatcher['ai_orchestrator'] = ai_orchestrator
    dispatcher['chat_settings_repository'] = chat_settings_repository
    dispatcher['cooldown_repository'] = cooldown_repository
    dispatcher['request_state_repository'] = request_state_repository
    dispatcher['reply_context_builder'] = reply_context_builder
    dispatcher['model_registry'] = model_registry
    dispatcher['status_service'] = status_service
    dispatcher['audit_log_repository'] = audit_log_repository

    return AppContainer(dispatcher=dispatcher, ai_orchestrator=ai_orchestrator, db=db)
