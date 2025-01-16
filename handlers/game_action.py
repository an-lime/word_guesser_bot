from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from databases.database_main import Database
from databases.models import Words
from keyboards.game_button import create_inline_game_keyboard
from middlewares.word_for_game import WordMiddleware
from services.alphabet import get_alphabet
from lexicon.body import display_hangman
from states.botStates import BotStates

router_game_action = Router()
router_game_action.callback_query.middleware(WordMiddleware())


@router_game_action.callback_query(F.data == 'start_game', StateFilter(default_state))
async def start_game(callback: CallbackQuery, word: Words, db: Database, state: FSMContext):
    keyboard = create_inline_game_keyboard(8, **get_alphabet())

    await db.user_in_game.add_game(id_user=str(callback.from_user.id), id_word=word.id_word, session=db.session)

    await callback.message.edit_text(
        text=f'{word.word} \n'
             f'{display_hangman(6)} \n'
             f'{word.description} \n'
             f'{"□" * len(word.word)} ',
        reply_markup=keyboard
    )
    await state.set_state(BotStates.in_game)


@router_game_action.callback_query(F.data == 'start_game')
async def try_start_game(callback: CallbackQuery):
    await callback.answer('Вы уже в игре!')


@router_game_action.callback_query()
async def game_letter(callback: CallbackQuery):
    await callback.answer(callback.data)
