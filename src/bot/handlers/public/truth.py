from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
from bot.utils.text import render_pretty_html

router = Router(name="public_truth")


@router.message(Command("truth"))
async def truth_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    replied = getattr(message, 'reply_to_message', None)
    if replied is None:
        await message.answer("Reply to a message to use /truth.")
        return
    claim_text = reply_context_builder.message_text(replied)
    if not claim_text:
        await message.answer("The replied message does not contain text to analyze.")
        return
    context = reply_context_builder.build_ancestor_context(replied)
    result = await ai_orchestrator.truth(chat_id=message.chat.id, claim_text=claim_text, context=context)
    for chunk in split_telegram_text(render_pretty_html(result), settings.telegram_message_max_len):
        await message.answer(chunk)
