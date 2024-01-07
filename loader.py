from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.enums.parse_mode import ParseMode
from decouple import config

# Создаем нашего бота и диспатчер, MemoryStorage хранилище состояний

# Здесь 'my_bot' - это уникальное имя вашего бота, а './locales' - путь к папке с файлами локализации

bot = Bot(token=config('BOT_TOKEN'), parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
