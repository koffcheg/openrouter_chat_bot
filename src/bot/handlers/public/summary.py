from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError
from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
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
    if not target_text.strip():
        await message.answer("Reply to a message or provide text after /sum.")
        return
    language_hint = detect_response_language(target_text, 'ru')
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
        result = await ai_orchestrator.summarize(chat_id=message.chat.id, target_text=target_text, context=context, language_hint=language_hint)
    except ProviderTimeoutError:
        await message.answer("The AI provider timed out. Please try again in a moment.", reply_to_message_id=target_reply_id)
        return
    except ProviderRateLimitError:
        await message.answer("The AI provider rate-limited the request. Please try again shortly.", reply_to_message_id=target_reply_id)
        return
    except ProviderUnavailableError:
        await message.answer("The AI provider is temporarily unavailable. Please try again later.", reply_to_message_id=target_reply_id)
        return
    except ProviderError:
        await message.answer("The AI provider returned an invalid response. Please try again.", reply_to_message_id=target_reply_id)
        return
    rendered = _summary_prefix(language_hint) + render_pretty_html(result)
    for chunk in split_telegram_text(rendered, settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=target_reply_id)
