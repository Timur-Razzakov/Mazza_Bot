from typing import List

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data import config
from data.data_classes import mailings_data, MailingData
from data.translations import ru_texts, user_language, _
from handlers.registration import determine_language
from keyboards import admin_kb, language_keyboard
from keyboards.admin_kb import cancel_markup
from keyboards.mailing_for_user_kb import mailing
from loader import bot
from states.mailing_state import MailingState
from utils.db import Users

mailing_router = Router(name=__name__)


# Создаем функцию для инициализации get_mailing_data
@sync_to_async
def get_mailing_data(user_id):
    if user_id not in mailings_data:
        mailings_data[user_id] = MailingData()
    return mailings_data[user_id]


@mailing_router.message(F.text == ru_texts['newsletter'])
async def cmd_mailing(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        await message.answer(ru_texts['select_user_for_mailing'],
                             reply_markup=mailing)
    else:
        await message.answer(ru_texts['admin_no_access'])


@mailing_router.message(lambda message: message.text in [
    ru_texts['mailing'],
    ru_texts['mailing_without_tariff'],
    ru_texts['mailing_with_tariff'],
])
async def handle_language_selection(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    mailing_data = await get_mailing_data(user_id)
    mailing_data.user_id = user_id
    """ :param has_tariff: Если True, возвращает пользователей с тарифом.
                           Если False, возвращает пользователей без тарифа.
                           Если None, возвращает всех пользователей."""
    if message.text == ru_texts['mailing_with_tariff']:
        mailing_data.has_tariff = True
    elif message.text == ru_texts['mailing_without_tariff']:
        mailing_data.has_tariff = False
    else:
        pass
    await message.answer(
        text=ru_texts['download_file'],
        reply_markup=admin_kb.cancel_markup)
    await state.set_state(MailingState.file_id)


@mailing_router.message(MailingState.file_id, (F.photo | F.document | F.video | F.text))
async def get_product_description(message: types.Message,
                                  session_maker: sessionmaker,
                                  state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        mailing_data = await get_mailing_data(user_id)
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif message.content_type == 'video':
            file_id = message.video.file_id
        elif message.content_type == 'video':  # Для документов
            file_id = message.document.file_id
        else:
            file_id = None
        print(234234, message.content_type)
        print(234234, file_id)
        mailing_data.file_id = file_id
        mailing_data.file_type = message.content_type
        await message.answer(text=(ru_texts['language']),
                             reply_markup=language_keyboard.mailing_language)
        await state.set_state(MailingState.lang)


@mailing_router.message(MailingState.lang)
@mailing_router.callback_query(lambda query: query.data in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"])
async def get_user_name_from_client(callback_query: types.CallbackQuery,
                                    session_maker: sessionmaker,
                                    state: FSMContext):
    user_id = callback_query.message.chat.id
    mailing_data = await get_mailing_data(user_id)
    # выводим относительно языка короткий вариант его наименования ru|uzb
    mailing_data.lang = determine_language(callback_query.data)
    await bot.send_message(chat_id=user_id, text=(ru_texts['write_mailing']),
                           reply_markup=cancel_markup)
    await state.set_state(MailingState.message_for_client)


@mailing_router.message(MailingState.message_for_client)
async def get_user_name_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    mailing_data = await get_mailing_data(user_id)
    mailing_data.message = message.text
    await state.clear()
    users = await Users.get_users_by_tariff_status(session_maker=session_maker, language=mailing_data.lang,
                                                   has_tariff=mailing_data.has_tariff)
    if users:
        await send_message_to_users(users=users, message=mailing_data.message,
                                    file_id=mailing_data.file_id,
                                    file_type=mailing_data.file_type)
        await message.answer(text='Рассылка закончилась.',
                             reply_markup=admin_kb.markup)
    else:
        await message.answer(text='Клиенты не найдены!',
                             reply_markup=admin_kb.markup)


async def send_message_to_users(users: List[Users], file_type: str, file_id: str, message: str):
    """
    Отправить сообщение списку пользователей.

    :param file_id:
    :param file_type:
    :param users: Список пользователей.
    :param message: Сообщение для отправки.
    """
    for user in users:
        try:
            if file_id is not None:
                data = {
                    'chat_id': user.user_id,
                    'caption': message,
                    file_type: file_id
                }
                att = getattr(bot, f'send_{file_type}')
                await att(**data)
            else:
                await bot.send_message(user.user_id, message)
        except Exception as e:
            # Обработка ошибок отправки
            print(f"Ошибка при отправке сообщения пользователю {user.user_id}: {e}")


async def get_users_by_lang(language, session_maker):
    """Получаем пользователей относительно указанного языка"""
    users = await Users.get_users_by_language(language=language, session_maker=session_maker)
    return users
