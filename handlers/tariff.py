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
from keyboards.tariffs_kb import get_tariffs, tariffs_kb, update_tariff_kb
from loader import bot
from states.mailing_state import MailingState
from states.tariff_state import TariffState, AddTariffState
from utils.db import Users, Tariffs

tariff_router = Router(name=__name__)


class TariffData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.tariff_id = None
        self.tariffs_name = None
        self.description = None
        self.price = None

    def reset(self):
        self.user_id = None
        self.tariff_id = None
        self.tariffs_name = None
        self.description = None
        self.price = None


tariffs_data = {}


# Создаем функцию для инициализации get_course_data
@sync_to_async
def get_tariff_data(user_id):
    if user_id not in tariffs_data:
        tariffs_data[user_id] = TariffData()
    return tariffs_data[user_id]


@tariff_router.message(F.text == ru_texts['add_tariff'])
async def cmd_add_tariff(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in config.ADMIN_ID:
        await message.answer(ru_texts['tariff_name'],
                             reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddTariffState.tariffs_name)
    else:
        await message.answer(ru_texts['admin_no_access'])


@tariff_router.message(AddTariffState.tariffs_name)
async def get_tariffs_name(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    tariff_name = message.text.upper()

    if await is_valid_str_only(tariff_name):
        if str(user_id) in config.ADMIN_ID:
            # Проверяем есть ли в бд такая страна
            tariff_id = await get_tariff_id(tariff_name, session_maker)
            if tariff_id is None:
                tariff = await get_tariff_data(user_id)
                tariff.user_id = user_id
                tariff.tariff_name = tariff_name

                await message.answer(ru_texts['tariff_price'],
                                     reply_markup=admin_kb.cancel_markup)
                await state.set_state(AddTariffState.price)
            else:
                await message.answer(ru_texts['already_exists'],
                                     reply_markup=admin_kb.markup)
                await state.clear()
                return
        else:
            await message.answer(ru_texts['admin_no_access'])
            await state.clear()
    else:
        await message.answer(ru_texts['tariff_name_must_be_string'])


@tariff_router.message(AddTariffState.price)
async def get_tariffs_price(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in config.ADMIN_ID:
        if await is_valid_int_or_float(message.text):
            tariff = await get_tariff_data(user_id)
            tariff.price = message.text
            await message.answer(ru_texts['tariff_description'],
                                 reply_markup=admin_kb.cancel_markup)
            await state.set_state(AddTariffState.description)
        else:
            await message.answer(ru_texts['enter_correct_cost'])
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@tariff_router.message(AddTariffState.description)
async def get_tariff_description(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in config.ADMIN_ID:
        tariff = await get_tariff_data(user_id)
        tariff.description = message.text
        if tariff.tariff_id is not None:
            update_fields = {
                "tariffs_name": str(tariff.tariff_name),
                "price": float(tariff.price),
                "description": str(tariff.description),
            }
            await update_tariff(tariff_id=tariff.tariff_id,
                                 session_maker=session_maker,
                                 **update_fields)
            # После завершения использования, создаём новый экземпляр для очистки старого
            tariff.reset()
            text_for_message = ru_texts['data_updated']
        else:
            await save_tariff(tariff_name=tariff.tariff_name,
                              price=float(tariff.price),
                              description=tariff.description,
                              session_maker=session_maker)
            tariff.reset()
            text_for_message = ru_texts['saved_thank_you']
        await state.clear()  # очищаем state
        await message.answer(text_for_message, reply_markup=admin_kb.markup)
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@tariff_router.message(F.text == ru_texts['all_tariffs'])
async def cmd_get_all_tariffs(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in config.ADMIN_ID:
        # Получаем список тарифов
        tariffs = await get_tariffs(session_maker)
        # Вызываем функцию tariffs_kb, чтобы получить список тарифов и клавиатурный markup
        keyboard_markup = await tariffs_kb(tariffs, user_id)
        await state.set_state(TariffState.tariffs_name)
        await bot.send_message(chat_id=user_id,
                               text=ru_texts['choose_tariffs'],
                               reply_markup=keyboard_markup)
    else:
        await message.answer(ru_texts['admin_no_access'])


@tariff_router.message(TariffState.tariffs_name)
async def process_get_tariff_id(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.chat.id
    # Используем функцию для инициализации user_order
    tariff = await get_tariff_data(user_id)
    tariff_name = message.text
    tariff_info = await Tariffs.get_tariff_from_name(tariff_name, session_maker)
    tariff.tariff_id = tariff_info.id
    if tariff_name == ru_texts['back']:
        await message.answer(ru_texts['goodbye'], reply_markup=admin_kb.markup)
        await state.clear()
        # После завершения использования, создаём новый экземпляр для очистки старого
        tariff.reset()
        return
    else:
        text = await text_for_tariff_info(tariff_name=tariff_info.tariffs_name, price=tariff_info.price,
                                          description=tariff_info.description)

        await message.answer(text, reply_markup=update_tariff_kb(user_id))
        return


@tariff_router.callback_query(lambda query: query.data in ['update_tariff', 'delete_tariff'])
async def update_or_delete_tariff(callback_query: types.CallbackQuery, session_maker: sessionmaker,
                                  state: FSMContext):
    """Функция для обновления доставки"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    tariff = await get_tariff_data(user_id)
    if data == 'delete_tariff':
        await del_tariff(tariff.tariff_id, session_maker)
        await bot.send_message(user_id, ru_texts['tariff_deleted'], reply_markup=admin_kb.markup)
        await state.clear()
    elif data == 'update_tariff':
        await bot.send_message(user_id, ru_texts['tariff_name'],
                               reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddTariffState.tariffs_name)
    # удаляем сообщение с кнопкой, для избежания повторного нажатия
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)


@sync_to_async
def text_for_tariff_info(price, description, tariff_name):
    # собираем в таблицу для админа
    message_text = ''
    message_text += "<pre>"
    message_text += "{:<15} : {:<15}\n".format("Price", price)
    message_text += "{:<15} : {:<15}\n".format("Tariff", tariff_name)
    message_text += "{:<15} : {:<15}\n".format("Description", description)
    message_text += "</pre>"
    return message_text


@sync_to_async
def is_valid_str_only(text):
    """
    Проверяем что нам приходят только строки
    :param text:
    :return:
    """
    if text and not any(char.isdigit() for char in text):
        return True
    return False


async def get_tariff_id(tariff_name, session_maker):
    tariff_id = await Tariffs.get_tariff_from_name(tariffs_name=tariff_name, session_maker=session_maker)
    return tariff_id


async def save_tariff(tariff_name, description, price, session_maker):
    tariff = await Tariffs.create_tariff(
        tariffs_name=tariff_name,
        description=description,
        price=price,
        session_maker=session_maker)
    return tariff


@sync_to_async
def is_valid_int_or_float(text):
    try:
        float_value = float(text)
        return True
    except ValueError:
        return False


async def del_tariff(tariff_id, session_maker):
    """
    Удаляем тариф
    :param tariff_id:
    :param session_maker:
    :return:
    """
    tariff = await Tariffs.delete_tariff_by_id(tariff_id, session_maker)
    return tariff


async def update_tariff(tariff_id, session_maker, **update_fields):
    """
       Асинхронно обновляет информацию о конкретном тарифе.

       :param tariff_id: ID тарифа, который нужно обновить.
       :param session_maker: Фабрика сессий SQLAlchemy.
       :param update_fields: Ключевые аргументы, представляющие поля для обновления и их новые значения.
       :return: Обновленный объект продукта или None, если продукт не существует."""

    updated_tariff = await Tariffs.update_tariff(
        tariff_id=tariff_id,
        session_maker=session_maker,
        **update_fields
    )
    return updated_tariff
