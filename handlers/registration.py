from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data.config import Image_PATH
from data.data_classes import registration_data, RegistrationData
from data.translations import _, ru_texts, user_language
from keyboards import inline_button, default_kb
from keyboards.default_kb import cancel_markup, contact_keyboard
from loader import bot
from states import ClientDataState
from utils.db import Users

registration_router = Router(name=__name__)


# Создаем функцию для инициализации get_user_data
async def get_user_data(user_id):
    if user_id not in registration_data:
        registration_data[user_id] = RegistrationData()
    return registration_data[user_id]


@registration_router.message(lambda message: message.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"])
async def handle_language_selection(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    user_data.user_id = user_id

    # выводим относительно языка короткий вариант его наименования ru|uzb
    user_data.lang = determine_language(message.text)
    user_language[user_id] = user_data.lang
    # Получаем язык пользователя и отправляем соответствующее сообщение
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['user_name'], selected_language),
                         reply_markup=await cancel_markup(user_id, session_maker))
    await state.set_state(ClientDataState.user_name)


# фото для главной страницы, прописал так чтобы ускорить обрабоку
photo = 'AgACAgIAAxkBAAIcUmW6LBUYAAHIYH5PC17eWHmvR-nqbAACaNMxG6Tw0UnxYwYIruEKugEAAwIAA3kAAzQE'
@registration_router.message(ClientDataState.user_name)
async def get_user_name_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    # photo = message.photo[-1].file_id
    # print(photo)
    user_data = await get_user_data(user_id)
    user_data.user_name = message.text
    selected_language = user_data.lang  # По умолчанию, если язык не задан, используем 'ru'
    if message.text == _(ru_texts['cancel_x'], selected_language):
        # если нажали отмена, то сохраняем пользователя в бд без номера ( имя с тг сами взяли)
        user_name = message.chat.first_name
        await save_user(user_id=user_data.user_id,
                        user_name=user_name,
                        user_lang=selected_language,
                        session_maker=session_maker,
                        user_number=None,
                        )
        await state.clear()

        text = _(ru_texts['bot_greeting'], selected_language)
        reply_markup = await inline_button.action_for_get_info(user_id, session_maker)
        await bot.send_photo(user_id,
                             photo=photo,
                             caption=text,
                             reply_markup=reply_markup)
    else:
        text = _(ru_texts['user_number'], selected_language)
        reply_markup = contact_keyboard(user_id)
        await state.set_state(ClientDataState.user_number)
        await message.answer(text=text,
                             reply_markup=reply_markup)


@registration_router.message(ClientDataState.user_number)
async def get_user_number_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    user_data = await get_user_data(user_id)
    selected_language = user_data.lang  # По умолчанию, если язык не задан, используем 'ru'
    await state.clear()
    if message.text:
        user_data.user_number = message.text
    else:
        user_data.user_number = message.contact.phone_number

    await save_user(user_id=user_data.user_id,
                    user_name=user_data.user_name,
                    user_lang=selected_language,
                    session_maker=session_maker,
                    user_number=user_data.user_number)

    await bot.send_photo(user_id,
                         photo=photo,
                         caption=_(ru_texts['bot_greeting'], selected_language),
                         reply_markup=await inline_button.action_for_get_info(user_id, session_maker), )


@registration_router.callback_query(lambda query: query.data in ['ru', 'uzb'])
async def get_language(callback_query: types.CallbackQuery,
                       session_maker: sessionmaker,
                       state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.message.chat.id
    user_language[user_id] = callback_query.data
    update_fields = {
        "lang": callback_query.data,
    }
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    try:
        await update_user(user_id=user_id,
                          session_maker=session_maker,
                          **update_fields)
        await bot.send_message(user_id, text=_(ru_texts['changed_lang'], selected_language),
                               reply_markup=await default_kb.create_default_markup(user_id, session_maker))
    except ValueError:
        await bot.send_message(user_id,
                               text=f"{_(ru_texts['registration'], selected_language)}\n{_(ru_texts['user_name'], selected_language)}",
                               reply_markup=await cancel_markup(user_id, session_maker))
        await state.set_state(ClientDataState.user_name)


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
