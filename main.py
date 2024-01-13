import asyncio
import logging
import sys
from decouple import config as env_config
from aiogram.types import BotCommand
from sqlalchemy import URL
from telethon import TelegramClient

from data import config
from handlers import bot_commands
from handlers.admin import admin_router
from handlers.click_cancel_or_back import cancel_router
from handlers.product import course_router
from handlers.default import default_router
from handlers.feedback import feedback_router
from handlers.mailing import mailing_router
from handlers.registration import registration_router
from handlers.tariff import tariff_router
from loader import dp, bot
from utils.db import create_async_engine, get_session_maker, proceed_schemas, Base


# TODO: Написать тесты
async def main() -> None:
    # создаём боковую панель
    commands_for_bot = []
    for cmd in bot_commands:  # импортируем из handlers/init
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands=commands_for_bot)
    dp.include_router(registration_router)
    dp.include_router(cancel_router)
    dp.include_router(default_router)  # команды для старта и тд..
    dp.include_router(feedback_router)

    dp.include_router(admin_router)
    dp.include_router(mailing_router)
    dp.include_router(tariff_router)
    dp.include_router(course_router)

    # подключаемся к бд
    postgresql_url = URL.create(
        'postgresql+asyncpg',
        username=config.DB_USER,
        password=config.DB_PASS,
        database=config.DB_NAME,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    async_engine = create_async_engine(postgresql_url)
    session_maker = get_session_maker(async_engine)  # для работы с бд создаём сессии
    print(235442265467, session_maker)
    await proceed_schemas(async_engine, Base.metadata)
    await async_engine.dispose()  # решает проблему с event loop
    await dp.start_polling(bot, session_maker=session_maker, skip_updates=True)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
