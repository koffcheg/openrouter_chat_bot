from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError, UserInputError
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
from bot.utils.text import detect_response_language, identity_answer, is_identity_question, render_pretty_html

router = Router(name="public_ask")


@router.message(Command("ask"), F.text)
async def ask_command(
    message: Message,
    ai_orchestrator: AIOrchestrator,
    chat_settings_repository: ChatSettingsRepository,
    cooldown_repository: CooldownStateRepository,
    request_state_repository: RequestStateRepository,
    reply_context_builder: ReplyContextBuilder,
    settings: Settings,
) -> None:
    raw_text = message.text or ""
    _, _, rest = raw_text.partition(" ")

    chat_settings = await chat_settings_repository.get_or_create(message.chat.id)
    if chat_settings.is_paused:
        await message.answer("This chat is currently paused by an admin.")
        return

    user_id = message.from_user.id if message.from_user else 0
    remaining = await cooldown_repository.remaining_cooldown(chat_id=message.chat.id, user_id=user_id, cooldown_seconds=settings.default_user_cooldown_seconds)
    if remaining > 0:
        await message.answer(f"Cooldown active. Please wait {remaining} seconds before sending another request.")
        return

    language_hint = chat_settings.preferred_language if chat_settings.preferred_language != 'auto' else detect_response_language(rest or (getattr(message.reply_to_message, 'text', '') if getattr(message, 'reply_to_message', None) else ''), 'ru')

    if is_identity_question(rest):
        for chunk in split_telegram_text(identity_answer(language_hint), settings.telegram_message_max_len):
            await message.answer(chunk, reply_to_message_id=message.reply_to_message.message_id if getattr(message, 'reply_to_message', None) else message.message_id)
        return

    reply_context = ''
    target_reply_id = message.message_id
    if getattr(message, 'reply_to_message', None) is not None:
        target_reply_id = message.reply_to_message.message_id
        reply_context = reply_context_builder.message_text(message.reply_to_message)
        if not rest.strip():
            rest = 'Explain the replied message simply.' if language_hint == 'en' else 'Ответь по смыслу на сообщение, на которое ответили.'

    request_key = await request_state_repository.acquire(chat_id=message.chat.id, user_id=user_id)
    if request_key is None:
        await message.answer("You already have an active request in progress.")
        return

    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        answer = await ai_orchestrator.ask(chat_id=message.chat.id, text=rest, reply_context=reply_context, language_hint=language_hint)
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
    except ProviderError:
        await message.answer("The AI provider returned an invalid response. Please try again.")
        return
    finally:
        await request_state_repository.release(chat_id=message.chat.id, user_id=user_id, request_key=request_key)

    for chunk in split_telegram_text(render_pretty_html(answer), settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=target_reply_id)
