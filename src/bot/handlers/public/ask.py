from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError, UserInputError
from bot.i18n.messages import resolve_reply_language, text as i18n_text
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.repositories.quota_state import CooldownStateRepository
from bot.repositories.request_state import RequestStateRepository
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.services.telegram.reply_sender import send_html_chunks
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
    detected_language = detect_response_language(rest or (getattr(message.reply_to_message, 'text', '') if getattr(message, 'reply_to_message', None) else ''), 'ru')
    ui_language = resolve_reply_language(chat_settings.preferred_language, detected_language)
    if chat_settings.is_paused:
        await message.answer(i18n_text('paused', ui_language))
        return

    user_id = message.from_user.id if message.from_user else 0
    remaining = await cooldown_repository.remaining_cooldown(chat_id=message.chat.id, user_id=user_id, cooldown_seconds=settings.default_user_cooldown_seconds)
    if remaining > 0:
        await message.answer(i18n_text('cooldown', ui_language, seconds=remaining))
        return

    language_hint = ui_language

    if is_identity_question(rest):
        await send_html_chunks(
            message,
            identity_answer(language_hint),
            settings.telegram_message_max_len,
            reply_to_message_id=message.reply_to_message.message_id if getattr(message, 'reply_to_message', None) else message.message_id,
        )
        return

    reply_context = ''
    target_reply_id = message.message_id
    if getattr(message, 'reply_to_message', None) is not None:
        target_reply_id = message.reply_to_message.message_id
        reply_context = reply_context_builder.message_text(message.reply_to_message)
        if not rest.strip():
            rest = 'Explain the replied message simply.' if language_hint == 'en' else ('Поясни повідомлення, на яке відповіли, простими словами.' if language_hint == 'uk' else 'Ответь по смыслу на сообщение, на которое ответили.')

    request_key = await request_state_repository.acquire(chat_id=message.chat.id, user_id=user_id)
    if request_key is None:
        await message.answer(i18n_text('active_request', ui_language))
        return

    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        answer = await ai_orchestrator.ask(chat_id=message.chat.id, text=rest, reply_context=reply_context, language_hint=language_hint)
        await cooldown_repository.touch(chat_id=message.chat.id, user_id=user_id)
    except UserInputError as exc:
        await message.answer(str(exc))
        return
    except ProviderTimeoutError:
        await message.answer(i18n_text('provider_timeout', ui_language))
        return
    except ProviderRateLimitError:
        await message.answer(i18n_text('provider_rate_limit', ui_language))
        return
    except ProviderUnavailableError:
        await message.answer(i18n_text('provider_unavailable', ui_language))
        return
    except ProviderError:
        await message.answer(i18n_text('provider_invalid', ui_language))
        return
    finally:
        await request_state_repository.release(chat_id=message.chat.id, user_id=user_id, request_key=request_key)

    await send_html_chunks(message, render_pretty_html(answer), settings.telegram_message_max_len, reply_to_message_id=target_reply_id)
