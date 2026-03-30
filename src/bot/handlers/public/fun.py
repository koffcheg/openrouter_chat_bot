from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text

router = Router(name="public_fun")


@router.message(Command("fun"))
async def fun_command(message: Message, ai_orchestrator: AIOrchestrator, reply_context_builder: ReplyContextBuilder, settings) -> None:
    raw_text = message.text or ''
    _, _, text = raw_text.partition(' ')
    if not text.strip() and getattr(message, 'reply_to_message', None) is not None:
        text = reply_context_builder.message_text(message.reply_to_message)
        context = reply_context_builder.build_ancestor_context(message.reply_to_message)
    else:
        context = ''
    if not text.strip():
        await message.answer("Provide text after /fun or reply to a message.")
        return
    result = await ai_orchestrator.fun(chat_id=message.chat.id, text=text, context=context)
    for chunk in split_telegram_text(result, settings.telegram_message_max_len):
        await message.answer(chunk)
