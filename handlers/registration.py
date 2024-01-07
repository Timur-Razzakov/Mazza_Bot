from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data.translations import _, ru_texts, user_language
from keyboards import inline_button
from keyboards.default_kb import cancel_markup, contact_keyboard
from loader import bot
from states import ClientDataState
from utils.db import Users

registration_router = Router(name=__name__)


class RegistrationData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.user_name = None
        self.user_phone = None
        self.lang = None


registration_data = {}


# Создаем функцию для инициализации get_user_data
@sync_to_async
def get_user_data(user_id):
    if user_id not in registration_data:
        registration_data[user_id] = RegistrationData()
    return registration_data[user_id]


@registration_router.message(lambda message: message.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"])
async def handle_language_selection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    user_data.user_id = user_id
    # выводим относительно языка короткий вариант его наименования ru|uzb
    user_data.lang = determine_language(message.text)
    # Получаем язык пользователя и отправляем соответствующее сообщение
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    print(43252345234,selected_language)
    await message.answer(text=_(ru_texts['info_about_registration'], selected_language))
    await message.answer(text=_(ru_texts['user_name'], selected_language),
                         reply_markup=cancel_markup(user_id))
    await state.set_state(ClientDataState.user_name)


@registration_router.message(ClientDataState.user_name)
async def get_user_name_from_client(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_data = await get_user_data(user_id)
    user_data.user_name = message.text
    selected_language = user_data.lang  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['user_number'], selected_language),
                         reply_markup=await contact_keyboard(user_id))
    await state.set_state(ClientDataState.user_number)


@registration_router.message(ClientDataState.user_number, F.contact)
async def get_user_number_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    user_data = await get_user_data(user_id)
    if message.text:
        user_data.user_number = message.text
    else:
        user_data.user_number = message.contact.phone_number

    selected_language = user_data.lang  # По умолчанию, если язык не задан, используем 'ru'
    await state.clear()
    await save_user(user_id=user_data.user_id,
                    user_name=user_data.user_name,
                    user_lang=selected_language,
                    session_maker=session_maker,
                    user_number=user_data.user_number,

                    )
    await message.answer(text=_(ru_texts['bot_greeting'], selected_language),
                         reply_markup=inline_button.action_for_get_info(user_id))


@registration_router.callback_query(lambda query: query.data in ['ru', 'uzb'])
async def get_language(callback_query: types.CallbackQuery, session_maker: sessionmaker):
    user_id = callback_query.message.chat.id
    update_fields = {
        "lang": callback_query.data,
    }
    await update_user(user_id=user_id,
                      session_maker=session_maker,
                      **update_fields)
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    print(56565656, selected_language)
    # удаляем сообщение с кнопкой, для избежания повторного нажатия
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(user_id, text=_(ru_texts['lesson_text'], selected_language),
                           reply_markup=default_kb.create_default_markup(user_id))


async def save_user(user_id, user_name, user_number, user_lang, session_maker, tariff_id=None):
    user = await Users.create_user(
        name=user_name,
        user_id=user_id,
        phone=user_number,
        lang=user_lang,
        tariff_id=tariff_id,
        session_maker=session_maker)
    return user


async def update_user(user_id, session_maker, **update_fields):
    user_data = await Users.update_user(
        user_id=user_id,
        session_maker=session_maker,
        **update_fields)

    return user_data


def determine_language(message_text: str) -> str:
    if message_text == "🇺🇿 O'zbekcha":
        return 'uzb'
    elif message_text == "🇷🇺 Русский":
        return 'ru'
    else:
        return 'ru'  # По умолчанию возвращаем русский
