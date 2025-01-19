from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
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
from middlewares.throttling_middleware import ThrottlingMiddleware
from services.change_data import get_alphabet, get_letter_from_callback, try_guess_letter
from lexicon.body import display_hangman
from states.botStates import BotStates

router_game_action = Router()
router_game_action.callback_query.outer_middleware(ThrottlingMiddleware())
router_game_action.callback_query.middleware(GameMiddleware())


@router_game_action.callback_query(F.data == 'start_game', StateFilter(default_state))
async def start_game(callback: CallbackQuery, hidden_word: Words, db: Database, state: FSMContext):
    await state.update_data({'hidden_word': hidden_word})
    await state.update_data({'word_completion': LEXICON['hide_letter'] * len(hidden_word.word)})
    await state.update_data({'tries': 6})
    await state.update_data({'guessed_letters': ''})

    alphabet = await get_alphabet(word=hidden_word.word)
    keyboard = create_inline_game_keyboard(8, **alphabet)

    await db.user_in_game.add_game(id_user=str(callback.from_user.id), id_word=hidden_word.id_word, session=db.session)

    await callback.message.edit_text(
        text=f'{display_hangman(await state.get_value('tries'))} \n'
             f'{hidden_word.description} \n'
             f'{await state.get_value("word_completion")} ',
        reply_markup=keyboard
    )
    await state.set_state(BotStates.in_game)


@router_game_action.callback_query(F.data == 'start_game')
async def try_start_game(callback: CallbackQuery):
    await callback.answer(LEXICON['warn_you_in_game'])


@router_game_action.callback_query(StateFilter(BotStates.in_game), IsGuessLetter())
async def game_letter(callback: CallbackQuery, state: FSMContext, db: Database):
    if callback.data[-1] == '*':
        await callback.answer()
        return

    if check_word(word=(await state.get_value('hidden_word')).word, callback=callback):

        if get_letter_from_callback(callback=callback).lower() in await state.get_value('guessed_letters'):
            return

        await state.update_data({'guessed_letters': await state.get_value('guessed_letters') + get_letter_from_callback(
            callback=callback).lower()})
        print(await state.get_value('guessed_letters'))

        if get_letter_from_callback(callback=callback).lower() in (await state.get_value('hidden_word')).word.lower():
            await state.update_data(
                {'word_completion': try_guess_letter(letter=get_letter_from_callback(callback=callback).lower(),
                                                     word=(await state.get_value('hidden_word')).word,
                                                     word_completion=await state.get_value('word_completion'))})

            if LEXICON['hide_letter'] not in await state.get_value('word_completion'):
                await db.users.update_user(id_user=str(callback.from_user.id), points=await state.get_value('tries'),
                                           session=db.session)
                await db.user_in_game.stop_game(str(callback.from_user.id), session=db.session)

                await callback.message.edit_text(f'{LEXICON['word_guessed']}\n'
                                                 f'{await state.get_value('word_completion')}\n -- {(await state.get_value('hidden_word')).description}')

                keyboard = create_inline_game_keyboard(1, 'start_game')
                await callback.message.answer(text=LEXICON['start_new_game'],
                                              reply_markup=keyboard)
                await state.clear()
                return

        else:
            await state.update_data({'tries': await state.get_value('tries') - 1})
            if await state.get_value('tries') < 0:
                await state.update_data({'tries': 0})

            await callback.answer(LEXICON['wrong_letter'])
        print(await state.get_value('tries'))
        if await state.get_value('tries') == 0:
            try:
                await callback.message.edit_text(
                    text=f'{display_hangman(await state.get_value('tries'))} \n'
                         f'Загаданное слово -- {(await state.get_value("hidden_word")).word}\n\n'
                         f'{(await state.get_value("hidden_word")).description} \n'
                )
            except TelegramBadRequest:
                return await callback.answer()

            await db.user_in_game.stop_game(str(callback.from_user.id), session=db.session)

            keyboard = create_inline_game_keyboard(1, 'start_game')
            await callback.message.answer(text=LEXICON['start_new_game'],
                                          reply_markup=keyboard)
            await state.clear()
            return

        if await state.get_state() != BotStates.in_game:
            return await callback.answer()

        alphabet = await get_alphabet(word=(await state.get_value("hidden_word")).word,
                                      guessed_letter=await state.get_value('guessed_letters'))
        keyboard = create_inline_game_keyboard(8, **alphabet)
        try:
            await callback.message.edit_text(
                text=f'{display_hangman(await state.get_value('tries'))} \n'
                     f'{(await state.get_value("hidden_word")).description} \n'
                     f'{await state.get_value('word_completion')} ',
                reply_markup=keyboard
            )
        except TelegramBadRequest:
            return await callback.answer()


    else:
        await callback.answer(LEXICON['not_actual_game'])


@router_game_action.message()
async def another_message(message: Message):
    await message.delete()
