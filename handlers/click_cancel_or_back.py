from typing import List, Optional

from aiogram import types, Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import ru_texts, user_language, _, uzb_texts
from keyboards import default_kb, admin_kb
from loader import dp, bot
from utils.db import Users

cancel_router = Router(name=__name__)


@cancel_router.message(
    lambda message: message.text in [ru_texts['back'], uzb_texts['back'], ])
async def command_back(message: types.Message, state: FSMContext):
    """Назад для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['goodbye'], selected_language),
                         reply_markup=admin_kb.markup)


@cancel_router.message(
    lambda message: message.text in [uzb_texts['back_for_user'], ru_texts['back_for_user']])
async def command_back_for_user(message: types.Message, state: FSMContext):
    """Назад для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['goodbye'], selected_language),
                         reply_markup=default_kb.create_default_markup(user_id))


@cancel_router.message(
    lambda message: message.text in [uzb_texts['cancel_with_X'], ru_texts['cancel_with_X']])
async def command_cancel(message: types.Message, state: FSMContext):
    """Отмена для пользователя"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['operation_cancelled'], selected_language),
                         reply_markup=default_kb.create_default_markup(user_id))


@cancel_router.message(
    lambda message: message.text in [uzb_texts['cancel_admin'], ru_texts['cancel_admin']])
async def command_cancel(message: types.Message, state: FSMContext):
    """Отмена для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['operation_cancelled'], selected_language),
                         reply_markup=admin_kb.markup)
