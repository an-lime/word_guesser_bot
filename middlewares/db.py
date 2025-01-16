from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware

from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from databases.database_main import Database
from databases.models import Users, Words, UserInGame


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self.session = session

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        async with self.session() as session:
            db = Database(session=session, users=Users(), words=Words(), user_in_game=UserInGame())
            data['db'] = db
            return await handler(event, data)
