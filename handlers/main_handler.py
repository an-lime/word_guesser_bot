from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from databases.database_main import Database
from filters.game_filter import IsGuessLetter
from lexicon.lexicon import LEXICON
from keyboards.game_button import create_inline_game_keyboard
from states.botStates import BotStates

router_standard_command = Router()


@router_standard_command.message(CommandStart(), StateFilter(default_state))
async def command_start(message: Message, db: Database):
    keyboard = create_inline_game_keyboard(1, 'start_game')
    await message.answer(text=LEXICON['commands']['/start'],
                         reply_markup=keyboard)
    await db.users.add_user(id_user=str(message.from_user.id),
                            name=(
                                (str(message.from_user.first_name) + str(message.from_user.last_name)).replace(
                                    'None', '')),
                            session=db.session)


@router_standard_command.message(Command(commands='cancel'), StateFilter(BotStates.in_game))
async def command_cancel(message: Message, db: Database, state: FSMContext):
    await db.user_in_game.stop_game(str(message.from_user.id), session=db.session)
    await db.users.update_user(id_user=str(message.from_user.id), points=-4, session=db.session)

    keyboard = create_inline_game_keyboard(1, 'start_game')
    await message.answer(LEXICON['commands']['/cancel'], reply_markup=keyboard)
    await state.clear()


@router_standard_command.message(Command(commands='records'), StateFilter(default_state))
async def command_records(message: Message, db: Database):
    records = await db.users.show_users(id_user=str(message.from_user.id), session=db.session)
    await message.answer(records)


@router_standard_command.message()
async def another_message(message: Message):
    await message.delete()


@router_standard_command.callback_query(~StateFilter(BotStates.in_game), IsGuessLetter())
async def another_callback(callback: CallbackQuery):
    await callback.answer()
