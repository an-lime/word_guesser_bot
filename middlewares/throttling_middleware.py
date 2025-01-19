from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, CallbackQuery
from cachetools import TTLCache

CACHE = TTLCache(maxsize=10_000, ttl=0.5)

class ThrottlingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get('event_from_user')

        if user.id in CACHE:
            await event.answer('Не загружайте бота!', show_alert=True)
            return

        CACHE[user.id] = True

        return await handler(event, data)