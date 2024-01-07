from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data.translations import ru_texts, user_language, _
from utils.db import Products


async def get_products(session_maker):
    products = await Products.get_all_products(session_maker=session_maker)
    return products


# Реализована клавиатура для выбора тарифа
async def products_kb(products, user_id):
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    builder = ReplyKeyboardBuilder()  #
    [builder.button(text=product.product_name) for product in products]
    builder.button(text=_(ru_texts['back'], selected_language))
    builder.adjust(*[2] * len(products), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup


async def free_products(session_maker):
    products = await Products.get_all_free_products(session_maker=session_maker)
    return products


async def products_user_kb(products, user_id):
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    builder = ReplyKeyboardBuilder()  #
    [builder.button(text=product.product_name) for product in products]
    builder.button(text=_(ru_texts['back_for_user'], selected_language))
    builder.adjust(*[2] * len(products), 1)
    markup = builder.as_markup(resize_keyboard=True)
    return markup


def update_product_kb(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована клавиатура для обновления курсов
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['update'], selected_language),
                                     callback_data="update_product"),
                InlineKeyboardButton(text=_(ru_texts['delete'], selected_language),
                                     callback_data="delete_product"),
            ],
        ],
        resize_keyboard=True, one_time_keyboard=True)


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


def markup_ransom(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована дефолтная клавиатура
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_(ru_texts['agree_without_smile'], selected_language)),
                KeyboardButton(text=_(ru_texts['cancel_without_smile'], selected_language)),
            ],
        ],
        resize_keyboard=True)


def update_tariff_kb(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована клавиатура для обновления тарифов
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(ru_texts['update'], selected_language),
                                     callback_data="update_product"),
                InlineKeyboardButton(text=_(ru_texts['delete'], selected_language),
                                     callback_data="delete_product"),
            ],
        ],
        resize_keyboard=True, one_time_keyboard=True)
