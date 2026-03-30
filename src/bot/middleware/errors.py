from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        try:
            return await handler(event, data)
        except Exception:
            logger.exception('Unhandled bot exception')
            answer = getattr(event, 'answer', None)
            if callable(answer):
                try:
                    await answer('An unexpected error occurred. Please try again later.')
                except Exception:
                    logger.exception('Failed to send fallback error message')
            return None
