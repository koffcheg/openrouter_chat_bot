from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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
    if not text.strip():
        await message.answer("Provide text after /fun or reply to a message.")
        return
    language_hint = detect_response_language(text, 'ru')
    result = await ai_orchestrator.fun(chat_id=message.chat.id, text=text, context=context, language_hint=language_hint)
    for chunk in split_telegram_text(render_pretty_html(result), settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=target_reply_id)
