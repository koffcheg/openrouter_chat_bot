from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.core.exceptions import ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError, UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository
from bot.services.ai.orchestrator import AIOrchestrator
from bot.utils.telegram_split import split_telegram_text

router = Router(name="public_ask")


@router.message(Command("ask"), F.text)
async def ask_command(
    message: Message,
    ai_orchestrator: AIOrchestrator,
    chat_settings_repository: ChatSettingsRepository,
    cooldown_repository: CooldownStateRepository,
    request_state_repository: RequestStateRepository,
    settings: Settings,
) -> None:
    raw_text = message.text or ""
    _, _, rest = raw_text.partition(" ")

    chat_settings = await chat_settings_repository.get_or_create(message.chat.id)
    if chat_settings.is_paused:
        await message.answer("This chat is currently paused by an admin.")
        return

    user_id = message.from_user.id if message.from_user else 0
    remaining = await cooldown_repository.remaining_cooldown(
        chat_id=message.chat.id,
        user_id=user_id,
        cooldown_seconds=settings.default_user_cooldown_seconds,
    )
    if remaining > 0:
        await message.answer(f"Cooldown active. Please wait {remaining} seconds before sending another request.")
        return

    request_key = await request_state_repository.acquire(chat_id=message.chat.id, user_id=user_id)
    if request_key is None:
        await message.answer("You already have an active request in progress.")
        return

    try:
        answer = await ai_orchestrator.ask(chat_id=message.chat.id, text=rest)
        await cooldown_repository.touch(chat_id=message.chat.id, user_id=user_id)
    except UserInputError as exc:
        await message.answer(str(exc))
        return
    except ProviderTimeoutError:
        await message.answer("The AI provider timed out. Please try again in a moment.")
        return
    except ProviderRateLimitError:
        await message.answer("The AI provider rate-limited the request. Please try again shortly.")
        return
    except ProviderUnavailableError:
        await message.answer("The AI provider is temporarily unavailable. Please try again later.")
        return
    finally:
        await request_state_repository.release(chat_id=message.chat.id, user_id=user_id, request_key=request_key)

    for chunk in split_telegram_text(escape(answer), settings.telegram_message_max_len):
        await message.answer(chunk)
