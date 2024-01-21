from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data.translations import ru_texts, user_language, _

# Реализована клавиатура админа
markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=ru_texts['home']),
            KeyboardButton(text=ru_texts['newsletter']),
        ],
        [
            KeyboardButton(text=ru_texts['add_course']),
            KeyboardButton(text=ru_texts['all_courses'])
        ],
        [
            KeyboardButton(text=ru_texts['add_tariff']),
            KeyboardButton(text=ru_texts['all_tariffs'])
        ],
        [
            KeyboardButton(text=ru_texts['download_excel']),
        ],
    ],
    resize_keyboard=True, one_time_keyboard=True)

# Реализована клавиатура команды отмена
cancel_markup = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text=ru_texts['cancel_admin']),

    ],
],
    resize_keyboard=True, one_time_keyboard=True)
