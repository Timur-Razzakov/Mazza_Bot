from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.translations import ru_texts, user_language, _


def action_for_get_info(user_id):
    """Инлайн кнопки, для получения информации о проекте"""
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['get_bonus_lesson'], selected_language),
                                     callback_data="get_bonus_lesson"),
            ],
            [
                InlineKeyboardButton(text=_(ru_texts['join_course'], selected_language),
                                     callback_data="join_course"),
            ]
        ], resize_keyboard=True,
    )


def action_for_select_free_course_or_not(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['yes'], selected_language),
                                     callback_data="yes"),
            ],
            [
                InlineKeyboardButton(text=_(ru_texts['no'], selected_language),
                                     callback_data="no"),
            ]
        ], resize_keyboard=True,
    )
