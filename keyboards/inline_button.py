from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.translations import ru_texts, user_language, _
from utils.db.utils import get_user_language


async def action_for_get_info(user_id, session_maker):
    """Инлайн кнопки, для получения информации о проекте"""
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['get_bonus_lesson'], user_lang),
                                     callback_data="get_bonus_lesson"),
            ],
            [
                InlineKeyboardButton(text=_(ru_texts['join_course'], user_lang, ),
                                     url="https://t.me/+ZQ1pvhiAJnwxOThi",
                                     callback_data="join_course"),
            ]
        ], resize_keyboard=True,
    )


async def action_for_select_free_course_or_not(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['yes'], user_lang),
                                     callback_data="yes"),
            ],
            [
                InlineKeyboardButton(text=_(ru_texts['no'], user_lang),
                                     callback_data="no"),
            ]
        ], resize_keyboard=True,
    )


async def join_group_markup(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Реализована клавиатура команды Помощь
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['join_course'], user_lang, ),
                                     url="https://t.me/+ZQ1pvhiAJnwxOThi",
                                     callback_data="join_course"),
            ]
        ], resize_keyboard=True,
    )