from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data.translations import ru_texts, user_language, _


def cancel_markup(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    # Реализована клавиатура команды отмена
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=_(ru_texts['cancel_with_X'], selected_language))

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


def create_default_markup(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'

    # Реализована дефолтная клавиатура
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_(ru_texts['about_instar'], selected_language)),
                KeyboardButton(text=_(ru_texts['suitable_for_me'], selected_language)),

            ],
            [
                KeyboardButton(text=_(ru_texts['free_materials'], selected_language)),
                KeyboardButton(text=_(ru_texts['course_questions'], selected_language)),
            ],
            [
                KeyboardButton(text=_(ru_texts['earn_after_training'], selected_language)),
                KeyboardButton(text=_(ru_texts['help'], selected_language)),
            ],
            [
                KeyboardButton(text=_(ru_texts['tariffs'], selected_language)),
            ]
        ],
        resize_keyboard=True)


def only_help_markup(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'

    # Реализована клавиатура команды Помощь
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ru_texts['support_department'], ),

            ],
        ],

        resize_keyboard=True, one_time_keyboard=True)


async def contact_keyboard(user_id):
    # Определяем язык пользователя
    selected_language = user_language.get(user_id, "ru")
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_(ru_texts['get_number'], selected_language), request_contact=True, ),
                # KeyboardButton(text=_(ru_texts['back_for_user'], selected_language))
            ]
        ],
        resize_keyboard=True,
    )
