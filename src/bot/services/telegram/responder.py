from aiogram.types import Message


async def reply_text(message: Message, text: str) -> None:
    await message.answer(text)
