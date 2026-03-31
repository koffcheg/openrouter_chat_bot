from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from bot.bootstrap import build_application
from bot.config.logging import configure_logging
from bot.config.settings import get_settings
from bot.services.telegram.command_setup import register_bot_commands


async def run() -> None:
    settings = get_settings()
    configure_logging(settings)
    logging.getLogger(__name__).info("Starting bot")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=settings.telegram_parse_mode),
    )
    container = await build_application(settings)
    try:
        await register_bot_commands(bot)
        await container.dispatcher.start_polling(
            bot,
            allowed_updates=settings.polling_allowed_updates_list,
            drop_pending_updates=settings.polling_drop_pending_updates,
        )
    finally:
        await bot.session.close()
        await container.db.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
