from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts

mailing = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=ru_texts['mailing']),
            KeyboardButton(text=ru_texts['mailing_without_tariff'], ),
            KeyboardButton(text=ru_texts['mailing_with_tariff']),
        ],
        [KeyboardButton(text=ru_texts['back']), ]
    ],
    resize_keyboard=True)
