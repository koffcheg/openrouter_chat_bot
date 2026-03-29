from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.exceptions import ProviderError, UserInputError
from bot.services.ai.orchestrator import AIOrchestrator

router = Router(name="public_ask")


@router.message(Command("ask"), F.text)
async def ask_command(message: Message, ai_orchestrator: AIOrchestrator) -> None:
    raw_text = message.text or ""
    command, _, rest = raw_text.partition(" ")
    del command
    try:
        answer = await ai_orchestrator.ask(chat_id=message.chat.id, text=rest)
    except UserInputError as exc:
        await message.answer(str(exc))
        return
    except ProviderError:
        await message.answer("The AI provider is unavailable right now. Please try again later.")
        return

    await message.answer(answer)
