from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts, user_language, _


def checked(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['agree_without_smile'], selected_language),
                                     callback_data="agree"),
                InlineKeyboardButton(text=_(ru_texts['cancel_without_smile'], selected_language),
                                     callback_data="cancel"),
            ]
        ], resize_keyboard=True,
    )


def markup_watch_video(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['confirm'], selected_language), callback_data="conf"),
                InlineKeyboardButton(text=_(ru_texts['confirm_2'], selected_language),
                                     callback_data="conf_2"),
            ]
        ], resize_keyboard=True,
    )


def markup_checked_watching_video(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['watched'], selected_language), callback_data="watched"),
                InlineKeyboardButton(text=_(ru_texts['not_watched'], selected_language),
                                     callback_data="not_watched"),
            ]
        ], resize_keyboard=True,
    )



