from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data.translations import ru_texts, user_language, _
from utils.db import Tariffs


async def get_tariffs(session_maker):
    tariffs = await Tariffs.get_all_tariffs(session_maker=session_maker)
    return tariffs


# Реализована клавиатура для выбора тарифа
async def tariffs_kb(tariffs, user_id):
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    builder = ReplyKeyboardBuilder()  #
    [builder.button(text=tariff.tariffs_name) for tariff in tariffs]
    builder.button(text=_(ru_texts['back'], selected_language))
    builder.adjust(*[2] * len(tariffs), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup


async def tariffs_user_kb(tariffs, user_id):
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    builder = ReplyKeyboardBuilder()  #
    [builder.button(text=f"{tariff.tariffs_name} | {tariff.price} UZS") for tariff in tariffs]
    builder.button(text=_(ru_texts['back_for_user'], selected_language))
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
