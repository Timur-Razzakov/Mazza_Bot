from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.enums.parse_mode import ParseMode
from decouple import config
from telethon import TelegramClient

# Создаем нашего бота и диспатчер, MemoryStorage хранилище состояний

# Здесь 'my_bot' - это уникальное имя вашего бота, а './locales' - путь к папке с файлами локализации
api_id = int(config('API_ID'))
api_hash = str(config('API_HASH'))
bot = Bot(token=config('BOT_TOKEN'), parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Telethon клиент
telethon_client = TelegramClient('session_name', api_id, api_hash)
