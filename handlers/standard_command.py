from aiogram import Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from databases.database_main import Database
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

@router_standard_command.message(CommandStart())
async def try_command_start(message: Message):
    await message.delete()

@router_standard_command.message(Command(commands='cancel'), StateFilter(BotStates.in_game))
async def command_cancel(message: Message, db: Database, state: FSMContext):
    await db.user_in_game.stop_game(str(message.from_user.id), session=db.session)
    await message.answer('123')
    await state.clear()