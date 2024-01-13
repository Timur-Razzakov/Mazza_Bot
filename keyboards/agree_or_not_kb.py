from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts, user_language, _
from utils.db.utils import get_user_language


async def markup_send_descriptions(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Реализована дефолтная клавиатура
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=(ru_texts['cancel_with_smile'])),
            ],
        ],
        resize_keyboard=True)
