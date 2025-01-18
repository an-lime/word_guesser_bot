from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from databases.database_main import Database
from databases.models import Words
from filters.game_filter import check_word, IsGuessLetter
from keyboards.game_button import create_inline_game_keyboard
from lexicon.lexicon import LEXICON
from middlewares.db_data import GameMiddleware
from services.change_data import get_alphabet, get_letter_from_callback, try_guess_letter
from lexicon.body import display_hangman
from states.botStates import BotStates

router_game_action = Router()
router_game_action.callback_query.middleware(GameMiddleware())


@router_game_action.callback_query(F.data == 'start_game', StateFilter(default_state))
async def start_game(callback: CallbackQuery, hidden_word: Words, db: Database, state: FSMContext):
    await state.update_data({'hidden_word': hidden_word})
    await state.update_data({'word_completion': LEXICON['hide_letter'] * len(hidden_word.word)})
    await state.update_data({'tries': 6})
    await state.update_data({'guessed_letters': ''})

    del hidden_word
    hidden_word: Words = await state.get_value('hidden_word')
    word_completion: str = await state.get_value('word_completion')
    tries: int = await state.get_value('tries')

    alphabet = await get_alphabet(word=hidden_word.word)
    keyboard = create_inline_game_keyboard(8, **alphabet)

    await db.user_in_game.add_game(id_user=str(callback.from_user.id), id_word=hidden_word.id_word, session=db.session)

    await callback.message.edit_text(
        text=f'{display_hangman(tries)} \n'
             f'{hidden_word.description} \n'
             f'{word_completion} ',
        reply_markup=keyboard
    )
    await state.set_state(BotStates.in_game)


@router_game_action.callback_query(F.data == 'start_game')
async def try_start_game(callback: CallbackQuery):
    await callback.answer(LEXICON['warn_you_in_game'])


@router_game_action.callback_query(StateFilter(BotStates.in_game), IsGuessLetter())
async def game_letter(callback: CallbackQuery, state: FSMContext, db: Database):
    hidden_word: Words = await state.get_value('hidden_word')
    word_completion: str = await state.get_value('word_completion')
    tries: int = await state.get_value('tries')
    guessed_letters: str = await state.get_value('guessed_letters')

    if callback.data[-1] == '*':
        await callback.answer()
        return

    if check_word(word=hidden_word.word, callback=callback):

        guessed_letters += get_letter_from_callback(callback=callback).lower()

        if get_letter_from_callback(callback=callback).lower() in hidden_word.word.lower():
            word_completion = try_guess_letter(letter=get_letter_from_callback(callback=callback).lower(),
                                               word=hidden_word.word, word_completion=word_completion)

            if LEXICON['hide_letter'] not in word_completion:
                await callback.message.edit_text(f'{LEXICON['word_guessed']}\n'
                                                 f'{word_completion}\n -- {hidden_word.description}')
                await db.users.update_user(id_user=str(callback.from_user.id), points=tries, session=db.session)

                keyboard = create_inline_game_keyboard(1, 'start_game')
                await callback.message.answer(text=LEXICON['start_new_game'],
                                              reply_markup=keyboard)
                await state.clear()
                return

        else:
            tries -= 1

            await callback.answer(LEXICON['wrong_letter'])

        await state.update_data({'tries': tries})
        await state.update_data({'word_completion': word_completion})
        await state.update_data({'guessed_letters': guessed_letters})

        if tries == 0:
            await callback.message.edit_text(
                text=f'{display_hangman(tries)} \n'
                     f'Загаданное слово -- {hidden_word.word}\n\n'
                     f'{hidden_word.description} \n'
            )

            keyboard = create_inline_game_keyboard(1, 'start_game')
            await callback.message.answer(text=LEXICON['start_new_game'],
                                          reply_markup=keyboard)
            await state.clear()
            return

        alphabet = await get_alphabet(word=hidden_word.word, guessed_letter=guessed_letters)
        keyboard = create_inline_game_keyboard(8, **alphabet)
        await callback.message.edit_text(
            text=f'{display_hangman(tries)} \n'
                 f'{hidden_word.description} \n'
                 f'{word_completion} ',
            reply_markup=keyboard
        )

    else:
        await callback.answer(LEXICON['not_actual_game'])


@router_game_action.message()
async def another_message(message: Message):
    await message.delete()
