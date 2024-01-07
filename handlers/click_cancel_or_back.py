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
async def command_back(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """Назад для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['goodbye'], user_lang),
                         reply_markup=admin_kb.markup)


@cancel_router.message(
    lambda message: message.text in [uzb_texts['back_for_user'], ru_texts['back_for_user']])
async def command_back_for_user(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """Назад для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['goodbye'], user_lang),
                         reply_markup=await default_kb.create_default_markup(user_id, session_maker))


@cancel_router.message(
    lambda message: message.text in [uzb_texts['cancel_with_X'], ru_texts['cancel_with_X']])
async def command_cancel(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    print(234234234,  message.text)
    """Отмена для пользователя"""
    user_id = message.from_user.id
    print(656565656,user_id)
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    print(32423423,user_lang)
    await message.answer(text=_(ru_texts['operation_cancelled'], user_lang),
                         reply_markup=await default_kb.create_default_markup(user_id, sessionmaker))


@cancel_router.message(
    lambda message: message.text in [uzb_texts['cancel_admin'], ru_texts['cancel_admin']])
async def command_cancel(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """Отмена для админа"""
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['operation_cancelled'], user_lang),
                         reply_markup=admin_kb.markup)


async def get_user_language(user_id, session_maker):
    user = await Users.get_user(user_id=user_id,
                                session_maker=session_maker)
    return user
