from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from databases.database_main import Database
from databases.models import Words
from filters.game_filter import check_word
from keyboards.game_button import create_inline_game_keyboard
from middlewares.db_data import WordMiddleware
from services.change_data import get_alphabet, get_word_from_callback, get_letter_from_callback, try_guess_letter
from lexicon.body import display_hangman
from states.botStates import BotStates

router_game_action = Router()
router_game_action.callback_query.middleware(WordMiddleware())


@router_game_action.callback_query(F.data == 'start_game', StateFilter(default_state))
async def start_game(callback: CallbackQuery, hidden_word: Words, db: Database, state: FSMContext):
    await state.update_data({'hidden_word': hidden_word})
    await state.update_data({'word_completion': "□" * len(hidden_word.word)})
    await state.update_data({'try': 6})

    del hidden_word
    hidden_word: Words = await state.get_value('hidden_word')
    word_completion: str = await state.get_value('word_completion')
    tries: int = await state.get_value('try')

    alphabet = await get_alphabet(word=hidden_word.word)
    keyboard = create_inline_game_keyboard(8, **alphabet)

    await db.user_in_game.add_game(id_user=str(callback.from_user.id), id_word=hidden_word.id_word, session=db.session)

    await callback.message.edit_text(
        text=f'{hidden_word.word} \n'
             f'{display_hangman(tries)} \n'
             f'{hidden_word.description} \n'
             f'{word_completion} ',
        reply_markup=keyboard
    )
    await state.set_state(BotStates.in_game)


@router_game_action.callback_query(F.data == 'start_game')
async def try_start_game(callback: CallbackQuery):
    await callback.answer('Вы уже в игре!')


@router_game_action.callback_query(StateFilter(BotStates.in_game))
async def game_letter(callback: CallbackQuery, state: FSMContext):
    hidden_word: Words = await state.get_value('hidden_word')
    word_completion: str = await state.get_value('word_completion')
    tries: int = await state.get_value('try')

    if callback.data[-1] == '*':
        print(123)
        await callback.answer()
        return

    if check_word(word=hidden_word.word, callback=callback):

        if get_letter_from_callback(callback=callback).lower() in hidden_word.word.lower():
            word_completion = try_guess_letter(letter=get_letter_from_callback(callback=callback).lower(),
                                               word=hidden_word.word, word_completion=word_completion)
            await state.update_data({'word_completion': word_completion})

            alphabet = await get_alphabet(word=hidden_word.word, del_letter=word_completion)
            keyboard = create_inline_game_keyboard(8, **alphabet)

            await callback.message.edit_text(
                text=f'{hidden_word.word} \n'
                     f'{display_hangman(tries)} \n'
                     f'{hidden_word.description} \n'
                     f'{word_completion} ',
                reply_markup=keyboard
            )
        else:
            await callback.answer('такой буквы нет')

    else:
        await callback.answer('Данная игра не актуальна!')
