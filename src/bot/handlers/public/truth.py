from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError
from bot.i18n.messages import text as i18n_text
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.services.telegram.reply_sender import send_html_chunks
from bot.utils.text import detect_response_language, render_pretty_html

router = Router(name="public_truth")


def _truth_prefix(language: str) -> str:
    if language == 'en':
        return 'Claim analysis\n'
    if language == 'uk':
        return 'Перевірка твердження\n'
    return 'Проверка утверждения\n'


@router.message(Command("truth"))
async def truth_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    replied = getattr(message, 'reply_to_message', None)
    if replied is None:
        await message.answer(i18n_text('truth_reply_required', 'ru'))
        return
    claim_text = reply_context_builder.message_text(replied)
    language_hint = detect_response_language(claim_text, 'ru')
    if not claim_text:
        await message.answer(i18n_text('replied_no_text', language_hint))
        return
    context = reply_context_builder.build_ancestor_context(replied)
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        result = await ai_orchestrator.truth(chat_id=message.chat.id, claim_text=claim_text, context=context, language_hint=language_hint)
    except ProviderTimeoutError:
        await message.answer(i18n_text('provider_timeout', language_hint), reply_to_message_id=replied.message_id)
        return
    except ProviderRateLimitError:
        await message.answer(i18n_text('provider_rate_limit', language_hint), reply_to_message_id=replied.message_id)
        return
    except ProviderUnavailableError:
        await message.answer(i18n_text('provider_unavailable', language_hint), reply_to_message_id=replied.message_id)
        return
    except ProviderError:
        await message.answer(i18n_text('provider_invalid', language_hint), reply_to_message_id=replied.message_id)
        return
    rendered = _truth_prefix(language_hint) + render_pretty_html(result)
    await send_html_chunks(message, rendered, settings.telegram_message_max_len, reply_to_message_id=replied.message_id)
