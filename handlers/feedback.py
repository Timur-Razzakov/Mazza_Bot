import asyncio

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from data import config
from data.translations import _, ru_texts, user_language
from handlers.default import actions, send_media_and_message, send_help_text_to_admin
from keyboards import default_kb
from keyboards.buttons_for_select import markup_watch_video, markup_checked_watching_video
from keyboards.default_kb import cancel_markup
from loader import bot, dp
from states.feedback_state import FeedbackState
from states.help_state import HelpState

feedback_router = Router(name=__name__)


class FeedbackData:
    # получаем text и контакт для связи
    def __init__(self):
        self.user_id = None
        self.feedback = None
        self.contact = None


feedback_data = {}


# Создаем функцию для инициализации
@sync_to_async
def get_feedback_text(user_id):
    if user_id not in feedback_data:
        feedback_data[user_id] = FeedbackData()
    return feedback_data[user_id]


@feedback_router.callback_query(lambda query: query.data == 'get_bonus_lesson')
async def cmd_send_text_media(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    selected_language = user_language.get(user_id, "ru")
    text_key, media_type, media_url = actions[callback_query.data]
    await send_media_and_message(user_id, media_type, media_url)
    await bot.send_message(
        chat_id=user_id,
        text=_(ru_texts[text_key], selected_language),
        reply_markup=markup_watch_video(user_id)
    )
    # Задержка перед отправкой следующего сообщения (например, 5 минут)
    await asyncio.sleep(10)  # 300 секунд = 5 минут 1200
    # Отправка сообщения после задержки
    await bot.send_message(user_id,
                           text=_(ru_texts['check_watching_video'], selected_language),
                           reply_markup=markup_checked_watching_video(user_id)
                           )


@feedback_router.callback_query(lambda query: query.data in ['conf', 'conf_2'])
async def get_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.message.chat.id
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    if callback_query.data in ["conf", "conf_2"]:
        # удаляем сообщение с кнопкой, для избежания повторного нажатия
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        await bot.send_message(user_id, text=_(ru_texts['lesson_text'], selected_language),
                               reply_markup=default_kb.create_default_markup(user_id))


@feedback_router.callback_query(lambda query: query.data in ['watched', 'not_watched'])
async def get_answe(callback_query: types.CallbackQuery, state: FSMContext):
    global text, reply_markup
    user_id = callback_query.message.chat.id
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    if callback_query.data == 'watched':
        text = _(ru_texts['user_is_watched'], selected_language)
        reply_markup = default_kb.cancel_markup(user_id)
    elif callback_query.data == 'not_watched':
        text = _(ru_texts['user_is_not_watched'], selected_language)
        reply_markup = default_kb.create_default_markup(user_id)
    # удаляем сообщение с кнопкой, для избежания повторного нажатия
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await bot.send_message(user_id, text=text,
                           reply_markup=reply_markup)
    await state.set_state(FeedbackState.feedback)


@feedback_router.message(FeedbackState.feedback)
async def get_messages_from_client(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    help_info = await get_feedback_text(user_id)
    help_info.text = message.text
    help_info.user_id = message.chat.id
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    await message.answer(text=_(ru_texts['enter_contact_info'], selected_language),
                         reply_markup=cancel_markup(user_id))
    await state.set_state(FeedbackState.contact)


@feedback_router.message(FeedbackState.contact)
async def get_contact_from_client(message: types.Message, state: FSMContext):
    admin = config.ADMIN_ID[0]
    user_id = message.chat.id
    help_info = await get_feedback_text(user_id)
    help_info.contact = message.text
    selected_language = user_language.get(user_id, "ru")  # По умолчанию, если язык не задан, используем 'ru'
    message_text = ''
    message_text += "<pre>"
    message_text += "{:<15} : {:<15}\n".format("Contact", help_info.contact)
    message_text += "{:<15} : {:<15}\n".format("Text", help_info.text)
    message_text += "</pre>"

    await send_help_text_to_admin(admin, message_text)
    await state.clear()
    await message.answer(
        text=_(ru_texts['feedback_is'], selected_language),
        reply_markup=default_kb.create_default_markup(user_id))
