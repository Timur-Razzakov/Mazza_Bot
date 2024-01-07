from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import _, ru_texts, user_language, uzb_texts
from handlers.click_cancel_or_back import get_user_language
from keyboards import default_kb, admin_kb, inline_button
from keyboards.default_kb import create_default_markup, cancel_markup
from keyboards.language_keyboard import language, language_inline
from keyboards.products_kb import products_user_kb, free_products
from keyboards.tariffs_kb import tariffs_user_kb, get_tariffs
from loader import bot, dp
from states.client_data import FreeCourseState, AllTariffsState
from states.help_state import HelpState
from utils.db import Users

default_router = Router(name=__name__)


async def send_help_text_to_admin(admin_chat_id, data_to_send):
    """Отправляем данные админу без подтверждения"""
    await bot.send_message(admin_chat_id, data_to_send)


class HelpData:
    # получаем text и контакт для связи
    def __init__(self):
        self.user_id = None
        self.text = None
        self.contact = None


help_data = {}


# Создаем функцию для инициализации get_help_text
@sync_to_async
def get_help_text(user_id):
    if user_id not in help_data:
        help_data[user_id] = HelpData()
    return help_data[user_id]


@dp.message(Command('language'))
async def cmd_start(message: types.Message, state: FSMContext, session_maker: sessionmaker, ):
    user_id = message.chat.id
    await state.clear()
    # Запрос выбора языка
    await message.answer("Tilni tanlang:\nВыберите язык:", reply_markup=language_inline)


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session_maker: sessionmaker, ):
    user_id = message.chat.id
    await state.clear()
    if str(user_id) in config.ADMIN_ID:
        await message.answer(ru_texts['answer_for_admin'],
                             reply_markup=admin_kb.markup)
        return
    # Получаем язык пользователя и отправляем соответствующее сообщение
    selected_language = await get_user_language(user_id, session_maker)
    if selected_language:
        await message.answer(text=_(ru_texts['bot_greeting'], selected_language),
                             reply_markup=await inline_button.action_for_get_info(user_id, session_maker),
                             reply=False)
        await message.answer(
            text="👋😃",  # Текст сообщения должен быть непустым, можно использовать пробел
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        # Запрос выбора языка
        await message.answer("Tilni tanlang:\n\nВыберите язык:", reply_markup=language)


#
# @dp.message(F.text == '/menu')
# async def cmd_menu(message: types.Message, state: FSMContext):
#     """Выводим главное меню с основными кнопками"""
#     user_id = message.chat.id
#     await state.clear()
#     if str(user_id) in config.ADMIN_ID:
#         pass
#         # await message.answer(ru_texts['answer_for_admin'],
#         #                      reply_markup=admin_kb.markup)
#     else:
#         # Запрос выбора языка
#         await message.answer("👋",
#                              reply_markup=default_kb.create_default_markup(user_id))


# Функция для отправки видео и сообщения
async def send_media_and_message(user_id, media_type=None, media_url=None):
    if media_url is not None:
        if media_type == 'video':
            await bot.send_video(chat_id=user_id, video=media_url)
        elif media_type == 'photo':
            await bot.send_photo(chat_id=user_id, photo=media_url)


# Словарь для сопоставления действий с текстами и URL видео
actions = {
    'get_bonus_lesson': ('preview_text_for_bonus_lesson', 'video', None),
    'join_course': ('join_course_text', 'photo', None)
}


@default_router.callback_query(lambda query: query.data == 'join_course')
async def cmd_send_text_media(callback_query: types.CallbackQuery, session_maker: sessionmaker, ):
    user_id = callback_query.message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    text_key, media_type, media_url = actions[callback_query.data]
    await send_media_and_message(user_id, media_type, media_url)
    await bot.send_message(
        chat_id=user_id,
        text=_(ru_texts[text_key], user_lang),
        reply_markup=await create_default_markup(user_id, session_maker)
    )


COMMANDS = {
    'course_questions': 'course_answer',
    'suitable_for_me': 'suitable_for_me_answer',
    'about_instar': 'about_instar_answer',
    'earn_after_training': 'earn_after_training_answer'
}
relevant_keys = ['course_questions', 'suitable_for_me', 'about_instar', 'earn_after_training']
relevant_commands = [uzb_texts[key] for key in relevant_keys] + [ru_texts[key] for key in relevant_keys]


@default_router.message(
    lambda message: message.text in relevant_commands)
async def cmd_answer_for_question(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """
    Получаем ответ на все кнопки при клике пользователем (кроме бесплатных материалов)
    :param message:
    :param state:
    :return:
    """
    user_id = message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    # Определение ключа для ответа
    response_key = next((key for key, value in uzb_texts.items() if value == message.text), None)
    if not response_key:
        response_key = next((key for key, value in ru_texts.items() if value == message.text), None)

    if response_key and response_key in COMMANDS:
        await message.answer(
            text=_(ru_texts[COMMANDS[response_key]], user_lang),
            reply_markup=await default_kb.create_default_markup(user_id, session_maker)
        )


@default_router.message(lambda message: message.text in [uzb_texts['help'], ru_texts['help']])
async def cmd_help(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """
    Получаем проблемную ситуацию от пользователя
    :param session_maker:
    :param message:
    :param state:
    :return:
    """
    user_id = message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['help_request_response'], user_lang),
                         reply_markup=await cancel_markup(user_id, session_maker))
    await state.set_state(HelpState.text)


@default_router.message(HelpState.text)
async def get_messages_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    help_info = await get_help_text(user_id)
    help_info.text = message.text
    help_info.user_id = message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['enter_contact_info'], user_lang),
                         reply_markup=await cancel_markup(user_id, session_maker))
    await state.set_state(HelpState.contact)


@default_router.message(HelpState.contact)
async def get_contact_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    admin = config.ADMIN_ID[0]
    user_id = message.chat.id
    help_info = await get_help_text(user_id)
    help_info.contact = message.text
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    message_text = ''
    message_text += "<pre>"
    message_text += "{:<15} : {:<15}\n".format("Contact", help_info.contact)
    message_text += "{:<15} : {:<15}\n".format("Text", help_info.text)
    message_text += "</pre>"

    await send_help_text_to_admin(admin, message_text)
    await state.clear()
    await message.answer(
        text=_(ru_texts['thank_you_for_data'], user_lang),
        reply_markup=await default_kb.create_default_markup(user_id, session_maker))


@default_router.message(
    lambda message: message.text in [uzb_texts['free_materials'], ru_texts['free_materials']])
async def cmd_get_free_materials(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    courses = await free_products(session_maker)
    keyboard_markup = await products_user_kb(courses, user_id, session_maker)
    await bot.send_message(chat_id=user_id,
                           text=ru_texts['choose_courses'],
                           reply_markup=keyboard_markup)
    await state.set_state(FreeCourseState.course_name)


# @default_router.message(FreeCourseState.course_name)
# async def process_direction(message: types.Message, state: FSMContext, session_maker: sessionmaker):
#     user_id = message.chat.id
#     # Используем функцию для инициализации user_order
#     product = await get_course_data(user_id)
#     product_name = message.text
#     product_info = await Products.get_product_from_name(product_name, session_maker)
#     if product_name == ru_texts['back']:
#         await message.answer(ru_texts['goodbye'], reply_markup=admin_kb.markup)
#         await state.clear()
#         # После завершения использования, создаём новый экземпляр для очистки старого
#         product.reset()
#         return

@default_router.message(
    lambda message: message.text in [uzb_texts['tariffs'], ru_texts['tariffs']])
async def cmd_get_tariffs(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    tariffs = await get_tariffs(session_maker)
    keyboard_markup = await tariffs_user_kb(tariffs, user_id, session_maker)
    await bot.send_message(chat_id=user_id,
                           text=ru_texts['choose_tariffs'],
                           reply_markup=keyboard_markup)
    await state.set_state(AllTariffsState.tariff_name)


@default_router.message(AllTariffsState.tariff_name)
async def cmd_select_tariff(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.chat.id
    tariff_name = message.text.split(" | ")[0]
    if tariff_name == ru_texts['back_for_user']:
        await message.answer(ru_texts['goodbye'],
                             reply_markup=await default_kb.create_default_markup(user_id, session_maker))
        await state.clear()
        return

    # # Используем функцию для инициализации user_order
    # product = await get_course_data(user_id)
    # product_info = await Products.get_product_from_name(product_name, session_maker)
    # if product_name == ru_texts['back']:
    #     await message.answer(ru_texts['goodbye'], reply_markup=admin_kb.markup)
    #     await state.clear()
    #     # После завершения использования, создаём новый экземпляр для очистки старого
    #     product.reset()
    #     return


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
