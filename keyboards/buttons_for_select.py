from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts, user_language, _
from utils.db.utils import get_user_language


async def checked(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['agree_without_smile'], user_lang),
                                     callback_data="agree"),
                InlineKeyboardButton(text=_(ru_texts['cancel_without_smile'], user_lang),
                                     callback_data="cancel"),
            ]
        ], resize_keyboard=True,
    )


async def markup_watch_video(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['confirm'], user_lang), callback_data="conf"),
                InlineKeyboardButton(text=_(ru_texts['confirm_2'], user_lang),
                                     callback_data="conf_2"),
            ]
        ], resize_keyboard=True,
    )


async def markup_checked_watching_video(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['watched'], user_lang), callback_data="watched"),
                InlineKeyboardButton(text=_(ru_texts['not_watched'], user_lang),
                                     callback_data="not_watched"),
            ]
        ], resize_keyboard=True,
    )
