from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data.translations import ru_texts, user_language, _
from utils.db import Tariffs, Users
from utils.db.utils import get_user_language


async def get_tariffs(session_maker):
    tariffs = await Tariffs.get_all_tariffs(session_maker=session_maker)
    return tariffs


async def products_kb(products, user_id, session_maker):
    user_lang = await Users.get_user(user_id=user_id,
                                     session_maker=session_maker)
    builder = ReplyKeyboardBuilder()  #
    if user_lang == 'uzb':
        [builder.button(text=product.product_name_uzb) for product in products]
    else:
        [builder.button(text=product.product_name) for product in products]
    builder.button(text=_(ru_texts['back'], user_lang))
    builder.adjust(*[2] * len(products), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup



# Реализована клавиатура для выбора тарифа
async def tariffs_kb(tariffs, user_id, session_maker):
    user_lang = await get_user_language(user_id, session_maker)
    builder = ReplyKeyboardBuilder()  #
    if user_lang == 'uzb':
        [builder.button(text=tariff.tariff_name_uzb) for tariff in tariffs]
    else:
        [builder.button(text=tariff.tariff_name) for tariff in tariffs]
    builder.button(text=_(ru_texts['back'], user_lang))
    builder.adjust(*[2] * len(tariffs), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup

async def get_tariffs_for_user(session_maker):
    tariffs = await Tariffs.get_all_tariffs(session_maker=session_maker)
    return tariffs


async def tariffs_user_kb(tariffs, user_id, session_maker):
    user_lang = await get_user_language(user_id, session_maker)
    builder = ReplyKeyboardBuilder()  #
    if user_lang == 'uzb':
        [builder.button(text=f"{tariff.tariff_name_uzb} | {tariff.price} UZS") for tariff in tariffs if
         tariff.tariff_name_uzb != '-']
    else:
        [builder.button(text=f"{tariff.tariff_name} | {tariff.price} UZS") for tariff in tariffs if
         tariff.tariff_name != '-']
    builder.button(text=_(ru_texts['back_for_user'], user_lang))
    builder.adjust(*[2] * len(tariffs), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup


def update_tariff_kb(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована клавиатура для обновления тарифов
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['update'], selected_language),
                                     callback_data="update_tariff"),
                InlineKeyboardButton(text=_(ru_texts['delete'], selected_language),
                                     callback_data="delete_tariff"),
            ],
        ],
        resize_keyboard=True, one_time_keyboard=True)
