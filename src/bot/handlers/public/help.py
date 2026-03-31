from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.constants import HELP_TEXT, START_TEXT

router = Router(name="public_help")

ABOUT_TEXT = """<b>CumxAI</b> — ассистент этого чата.

Что умеет:
• /ask [text] — ответить на вопрос
• /truth — проанализировать утверждение в ответе на сообщение
• /sum — кратко пересказать сообщение
• /fun [text] — лёгкий шуточный ответ

Важно:
• это не режим живой проверки интернета
• язык ответа обычно совпадает с языком пользователя
• если язык неясен, по умолчанию используется русский"""


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(START_TEXT)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command("about"))
async def about_command(message: Message) -> None:
    await message.answer(ABOUT_TEXT)
