from typing import List

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import ru_texts, user_language, _
from keyboards import admin_kb
from keyboards.admin_kb import cancel_markup
from keyboards.mailing_for_user_kb import mailing
from loader import bot
from states.mailing_state import MailingState
from utils.db import Users

mailing_router = Router(name=__name__)


class MailingData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.message = None
        self.lang = None
        self.has_tariff = None  # каким пользователям


mailings_data = {}


# Создаем функцию для инициализации get_mailing_data
@sync_to_async
def get_mailing_data(user_id):
    if user_id not in mailings_data:
        mailings_data[user_id] = MailingData()
    return mailings_data[user_id]


@mailing_router.message(F.text == ru_texts['newsletter'])
async def cmd_mailing(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in config.ADMIN_ID:
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
    await message.answer(text=(ru_texts['write_mailing']),
                         reply_markup=cancel_markup)
    await state.set_state(MailingState.message_for_client)


@mailing_router.message(MailingState.message_for_client)
async def get_user_name_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    mailing_data = await get_mailing_data(user_id)
    mailing_data.message = message.text
    await state.clear()
    users = await Users.get_users_by_tariff_status(session_maker, mailing_data.has_tariff)
    if users:
        await send_message_to_users(users, mailing_data.message)
        await message.answer(text='Рассылка закончилась.',
                             reply_markup=admin_kb.markup)
    else:
        await message.answer(text='Клиенты не найдены!',
                             reply_markup=admin_kb.markup)


async def send_message_to_users(users: List[Users], message: str):
    """
    Отправить сообщение списку пользователей.

    :param users: Список пользователей.
    :param message: Сообщение для отправки.
    """
    for user in users:
        try:
            await bot.send_message(user.user_id, message)
        except Exception as e:
            # Обработка ошибок отправки
            print(f"Ошибка при отправке сообщения пользователю {user.user_id}: {e}")


async def get_users_by_lang(language, session_maker):
    """Получаем пользователей относительно указанного языка"""
    users = await Users.get_users_by_language(language=language, session_maker=session_maker)
    return users
