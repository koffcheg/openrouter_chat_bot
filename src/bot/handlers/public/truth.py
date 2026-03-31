from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai.orchestrator import AIOrchestrator
from bot.services.telegram.context_builder import ReplyContextBuilder
from bot.utils.telegram_split import split_telegram_text
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
        await message.answer("Reply to a message to use /truth.")
        return
    claim_text = reply_context_builder.message_text(replied)
    if not claim_text:
        await message.answer("The replied message does not contain text to analyze.")
        return
    context = reply_context_builder.build_ancestor_context(replied)
    language_hint = detect_response_language(claim_text, 'ru')
    result = await ai_orchestrator.truth(chat_id=message.chat.id, claim_text=claim_text, context=context, language_hint=language_hint)
    rendered = _truth_prefix(language_hint) + render_pretty_html(result)
    for chunk in split_telegram_text(rendered, settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=replied.message_id)
