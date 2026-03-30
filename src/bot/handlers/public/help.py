from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.core.constants import HELP_TEXT, START_TEXT

router = Router(name="public_help")


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(START_TEXT)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(HELP_TEXT)
