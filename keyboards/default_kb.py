from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts, user_language, _
from handlers.click_cancel_or_back import get_user_language


async def cancel_markup(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Реализована клавиатура команды отмена
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=_(ru_texts['cancel_with_X'], user_lang))

        ],
    ],
        resize_keyboard=True, one_time_keyboard=True)


def back_markup(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована клавиатура команды отмена
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=_(ru_texts['back'], selected_language))

        ],
    ],
        resize_keyboard=True, one_time_keyboard=True)


async def create_default_markup(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Реализована дефолтная клавиатура
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_(ru_texts['about_instar'], user_lang)),
                KeyboardButton(text=_(ru_texts['suitable_for_me'], user_lang)),

            ],
            [
                KeyboardButton(text=_(ru_texts['free_materials'], user_lang)),
                KeyboardButton(text=_(ru_texts['course_questions'], user_lang)),
            ],
            [
                KeyboardButton(text=_(ru_texts['earn_after_training'], user_lang)),
                KeyboardButton(text=_(ru_texts['help'], user_lang)),
            ],
            [
                KeyboardButton(text=_(ru_texts['tariffs'], user_lang)),
            ]
        ],
        resize_keyboard=True)


async def only_help_markup(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Реализована клавиатура команды Помощь
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ru_texts['support_department'], ),

            ],
        ],

        resize_keyboard=True, one_time_keyboard=True)


async def contact_keyboard(user_id, session_maker):
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_(ru_texts['get_number'], user_lang), request_contact=True, ),
                # KeyboardButton(text=_(ru_texts['back_for_user'], user_lang))
            ]
        ],
        resize_keyboard=True,
    )
