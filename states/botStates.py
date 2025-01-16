from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    in_game = State()