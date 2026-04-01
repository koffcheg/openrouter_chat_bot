from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError
from bot.i18n.messages import text as i18n_text
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
from bot.utils.text import detect_response_language, render_pretty_html

router = Router(name="public_fun")


@router.message(Command("fun"))
async def fun_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    raw_text = message.text or ''
    _, _, text = raw_text.partition(' ')
    target_reply_id = message.message_id
    if not text.strip() and getattr(message, 'reply_to_message', None) is not None:
        text = reply_context_builder.message_text(message.reply_to_message)
        context = reply_context_builder.build_ancestor_context(message.reply_to_message)
        target_reply_id = message.reply_to_message.message_id
    else:
        context = ''
        if getattr(message, 'reply_to_message', None) is not None:
            target_reply_id = message.reply_to_message.message_id
    language_hint = detect_response_language(text, 'ru')
    if not text.strip():
        await message.answer(i18n_text('fun_need_text', language_hint))
        return
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        result = await ai_orchestrator.fun(chat_id=message.chat.id, text=text, context=context, language_hint=language_hint)
    except ProviderTimeoutError:
        await message.answer(i18n_text('provider_timeout', language_hint), reply_to_message_id=target_reply_id)
        return
    except ProviderRateLimitError:
        await message.answer(i18n_text('provider_rate_limit', language_hint), reply_to_message_id=target_reply_id)
        return
    except ProviderUnavailableError:
        await message.answer(i18n_text('provider_unavailable', language_hint), reply_to_message_id=target_reply_id)
        return
    except ProviderError:
        await message.answer(i18n_text('provider_invalid', language_hint), reply_to_message_id=target_reply_id)
        return
    for chunk in split_telegram_text(render_pretty_html(result), settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=target_reply_id)
