import asyncio
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config_data.config import BotConfig, load_config
from handlers.game_action import router_game_action
from handlers.main_handler import router_standard_command
from keyboards.main_menu import set_main_menu
from lexicon.lexicon import LEXICON_BOT_SETTING
from middlewares.db_data import DatabaseMiddleware

logging.basicConfig(level=logging.INFO,
                    format='%(filename)s: [%(funcName)s] %(lineno)d #%(levelname)-8s '
                           '[%(asctime)s] - %(name)s - %(message)s')

logger = logging.getLogger(__name__)


async def main():
    logger.info('Bot started...')

    config: BotConfig = load_config()
    engine = create_async_engine(url=config.db.url, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    storage = MemoryStorage()

    bot: Bot = Bot(token=config.tgBot.token,
                   default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_description(LEXICON_BOT_SETTING['bot_description'])
    await bot.set_my_short_description(LEXICON_BOT_SETTING['bot_short_description'])

    dp: Dispatcher = Dispatcher(storage=storage)

    await set_main_menu(bot=bot)

    dp.include_router(router_standard_command)
    dp.include_router(router_game_action)

    dp.update.middleware(DatabaseMiddleware(session=session))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
