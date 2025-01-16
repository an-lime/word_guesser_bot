from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext

from aiogram.types import TelegramObject

from states.botStates import BotStates


class WordMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        state: FSMContext = data.get("state")
        user_state = await state.get_state()

        if user_state != BotStates.in_game:
            data['word'] = await data['db'].words.get_random_word(session=data['db'].session)

        return await handler(event, data)
