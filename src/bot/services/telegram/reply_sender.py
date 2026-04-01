from __future__ import annotations

from bot.utils.telegram_split import split_telegram_text


async def send_html_chunks(message, text: str, max_len: int, *, reply_to_message_id: int | None = None) -> None:
    for chunk in split_telegram_text(text, max_len):
        await message.answer(chunk, reply_to_message_id=reply_to_message_id, parse_mode='HTML')
