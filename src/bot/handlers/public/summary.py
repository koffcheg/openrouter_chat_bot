from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text

router = Router(name="public_summary")


@router.message(Command("sum"))
async def summary_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    replied = getattr(message, 'reply_to_message', None)
    if replied is not None:
        target_text = reply_context_builder.message_text(replied)
        context = reply_context_builder.build_ancestor_context(replied)
    else:
        raw_text = message.text or ''
        _, _, target_text = raw_text.partition(' ')
        context = ''
    if not target_text.strip():
        await message.answer("Reply to a message or provide text after /sum.")
        return
    result = await ai_orchestrator.summarize(chat_id=message.chat.id, target_text=target_text, context=context)
    for chunk in split_telegram_text(escape(result), settings.telegram_message_max_len):
        await message.answer(chunk)
