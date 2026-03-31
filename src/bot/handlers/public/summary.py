from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
from bot.utils.text import detect_response_language, render_pretty_html, summary_template

router = Router(name="public_summary")


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
    result = await ai_orchestrator.summarize(chat_id=message.chat.id, target_text=target_text, context=context, language_hint=language_hint)
    rendered = summary_template(render_pretty_html(result), language_hint)
    for chunk in split_telegram_text(rendered, settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=target_reply_id)
