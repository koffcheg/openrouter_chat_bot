from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError
from bot.i18n.messages import text as i18n_text
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.services.telegram.reply_sender import send_html_chunks
from bot.utils.text import detect_response_language, render_pretty_html

router = Router(name="public_summary")


def _summary_prefix(language: str) -> str:
    if language == 'en':
        return 'Summary\n'
    if language == 'uk':
        return 'Коротко\n'
    return 'Кратко\n'


@router.message(Command("sum"))
async def summary_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    replied = getattr(message, 'reply_to_message', None)
    target_reply_id = message.message_id
    if replied is not None:
        target_text = reply_context_builder.message_text(replied)
        context = reply_context_builder.build_ancestor_context(replied)
        target_reply_id = replied.message_id
    else:
        raw_text = message.text or ''
        _, _, target_text = raw_text.partition(' ')
        context = ''
    language_hint = detect_response_language(target_text, 'ru')
    if not target_text.strip():
        await message.answer(i18n_text('sum_need_text', language_hint))
        return
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        result = await ai_orchestrator.summarize(chat_id=message.chat.id, target_text=target_text, context=context, language_hint=language_hint)
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
    rendered = _summary_prefix(language_hint) + render_pretty_html(result)
    await send_html_chunks(message, rendered, settings.telegram_message_max_len, reply_to_message_id=target_reply_id)
