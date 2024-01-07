from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

language = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text='🇷🇺 Русский', ),
        ],
    ],
    resize_keyboard=True)

language_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="uzb"),
            InlineKeyboardButton(text='🇷🇺 Русский', callback_data="ru"),
        ],
    ],
    resize_keyboard=True)
