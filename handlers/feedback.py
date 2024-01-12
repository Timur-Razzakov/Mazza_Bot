import asyncio

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import _, ru_texts
from handlers.default import send_help_text_to_admin
from keyboards import default_kb, inline_button
from keyboards.buttons_for_select import markup_checked_watching_video
from keyboards.default_kb import cancel_markup
from loader import bot
from states.feedback_state import FeedbackState
from utils.db import Products, Users
from utils.db.utils import get_user_language, delayed_message, send_product_info

feedback_router = Router(name=__name__)


@feedback_router.callback_query(lambda query: query.data == 'get_bonus_lesson')
async def cmd_send_text_media(callback_query: types.CallbackQuery, session_maker: sessionmaker, ):
    user_id = callback_query.message.chat.id
    await callback_query.answer()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    product_name = _(ru_texts['get_bonus_lesson'], user_lang).upper()
    markup = await default_kb.create_default_markup(user_id, session_maker)
    await send_product_info(product_name, user_id, session_maker, markup, message=None)
    # Задержка перед отправкой следующего сообщения
    """
    если ставлю await, то не срабатывает относительно указанного времени запуска, 
    без него работает отлично
    """
    asyncio.create_task(delayed_message(product_name=None, user_id=user_id,
                                        delay=1200,
                                        message=_(ru_texts['check_watching_video'], user_lang),
                                        session_maker=session_maker,
                                        markup=await markup_checked_watching_video(user_id, session_maker)))

    asyncio.create_task(
        delayed_message(product_name=ru_texts['pre_order'].upper(),
                        user_id=user_id,
                        delay=86400,
                        session_maker=session_maker,
                        message=None,
                        markup=await inline_button.join_group_markup(user_id, session_maker), ))
    asyncio.create_task(
        delayed_message(product_name=ru_texts['announcement'].upper(),
                        user_id=user_id,
                        delay=88000,
                        session_maker=session_maker,
                        message=None,
                        markup=await inline_button.join_group_markup(user_id, session_maker), ))
    asyncio.create_task(
        delayed_message(product_name=ru_texts['reasons_for_admission'].upper(),
                        user_id=user_id,
                        delay=172800,
                        session_maker=session_maker,
                        message=None,
                        markup=await inline_button.join_group_markup(user_id, session_maker)))


@feedback_router.callback_query(lambda query: query.data in ['conf', 'conf_2'])
async def get_answer(callback_query: types.CallbackQuery, session_maker: sessionmaker, state: FSMContext):
    user_id = callback_query.message.chat.id
    await callback_query.answer()
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # user_lang = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    if callback_query.data in ["conf", "conf_2"]:
        # удаляем сообщение с кнопкой, для избежания повторного нажатия
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(user_id, text=_(ru_texts['lesson_text'], user_lang),
                               reply_markup=await default_kb.create_default_markup(user_id, session_maker))


@feedback_router.callback_query(lambda query: query.data in ['watched', 'not_watched'])
async def get_answe(callback_query: types.CallbackQuery, session_maker: sessionmaker, state: FSMContext):
    global text, reply_markup
    await callback_query.answer()
    user_id = callback_query.message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # user_lang = user_language.get(user_id, "ru")
    if callback_query.data == 'watched':
        text = _(ru_texts['user_is_watched'], user_lang)
        reply_markup = await cancel_markup(user_id, session_maker)
    elif callback_query.data == 'not_watched':
        text = _(ru_texts['user_is_not_watched'], user_lang)
        reply_markup = default_kb.create_default_markup(user_id, session_maker)
    # удаляем сообщение с кнопкой, для избежания повторного нажатия
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(user_id, text=text,
                           reply_markup=reply_markup)
    await state.set_state(FeedbackState.feedback)


@feedback_router.message(FeedbackState.feedback)
async def get_messages_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    user_name = message.chat.username if message.chat.username else message.chat.first_name
    admin = config.ADMIN_ID[0]
    user: Users = await Users.get_user_by_id(user_id, session_maker)
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    message_text = ''
    message_text += "<pre>"
    message_text += "{:<15} : {:<15}\n".format("Contact", user.phone if user.phone is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("Username", user_name)
    message_text += "{:<15} : {:<15}\n".format("Text", message.text)
    message_text += "</pre>"
    await send_help_text_to_admin(admin, message_text)
    await state.clear()
    await message.answer(
        text=_(ru_texts['feedback_is'], user_lang),
        reply_markup=await default_kb.create_default_markup(user_id, session_maker))
