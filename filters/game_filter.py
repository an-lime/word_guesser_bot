from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from services.change_data import get_word_from_callback


def check_word(word: str, callback: CallbackQuery):
    return word == get_word_from_callback(callback=callback)

class IsGuessLetter(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        return 'char_' in callback.data