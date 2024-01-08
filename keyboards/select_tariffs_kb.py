from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.orm import sessionmaker

from data.translations import ru_texts, _
from handlers.click_cancel_or_back import get_user_language


async def action_for_get_paid(user_id: int, session_maker: sessionmaker):
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_(ru_texts['paid_pay_button'], user_lang), callback_data="paid_tariff"
                ),
                InlineKeyboardButton(
                    text=_(ru_texts['paid_back_button'], user_lang), callback_data="prev_action"
                ),
            ],
        ], resize_keyboard=True,
    )


async def action_for_get_paid_2(user_id: int, session_maker: sessionmaker):
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_(ru_texts['paid_transfer_button'], user_lang), callback_data="paid_action"
                ),
                InlineKeyboardButton(
                    text=_(ru_texts['paid_back_button'], user_lang), callback_data="prev_action"
                ),
            ],
        ], resize_keyboard=True,
    )


async def action_for_get_paid_3(user_id: int, session_maker: sessionmaker):
    user_lang = await get_user_language(user_id, session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_(ru_texts['paid_cancel_button'], user_lang), callback_data="prev_action"
                ),
            ],
        ], resize_keyboard=True,
    )


async def get_back_kb_button(user_id: int, session_maker: sessionmaker):
    # Создаём клавиатуру только с кнопкой "назад"
    user_lang = await get_user_language(user_id, session_maker)
    builder = ReplyKeyboardBuilder()
    builder.button(text=_(ru_texts['back_for_user'], user_lang))
    return builder.as_markup(resize_keyboard=True)
