from __future__ import annotations

from dataclasses import dataclass

from aiogram import Dispatcher

from bot.clients.openrouter import OpenRouterClient
from bot.config.settings import Settings
from bot.db.sqlite import connect, initialize_database
from bot.handlers.admin.control import router as admin_control_router
from bot.handlers.admin.status import router as admin_status_router
from bot.handlers.public.ask import router as ask_router
from bot.handlers.public.help import router as help_router
from bot.middleware.permissions import PermissionMiddleware
from bot.middleware.throttling import ThrottlingMiddleware
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository
from bot.services.ai.orchestrator import AIOrchestrator


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
        max_input_chars=settings.max_input_chars,
    )

    dispatcher = Dispatcher()
    dispatcher.update.middleware(PermissionMiddleware())
    dispatcher.update.middleware(ThrottlingMiddleware())
    dispatcher.include_router(help_router)
    dispatcher.include_router(ask_router)
    dispatcher.include_router(admin_control_router)
    dispatcher.include_router(admin_status_router)
    dispatcher["settings"] = settings
    dispatcher["ai_orchestrator"] = ai_orchestrator
    dispatcher["chat_settings_repository"] = chat_settings_repository
    dispatcher["cooldown_repository"] = cooldown_repository
    dispatcher["request_state_repository"] = request_state_repository

    return AppContainer(dispatcher=dispatcher, ai_orchestrator=ai_orchestrator, db=db)
