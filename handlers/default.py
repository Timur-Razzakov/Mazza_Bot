import os

import aiohttp
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker
import requests
from data import config
from data.config import BASE_DIR, Image_PATH
from data.data_classes import help_data, HelpData
from data.translations import _, ru_texts, user_language, uzb_texts
from handlers.product import get_course_data
from keyboards import default_kb, admin_kb, inline_button
from keyboards.default_kb import create_default_markup, cancel_markup, contact_keyboard, about_instar_markup
from keyboards.language_keyboard import language, language_inline
from keyboards.payment_confirm_reject_kb import get_payment_confirm_reject_markup, PayConfirmCallback, \
    PayConfirmAction
from keyboards.products_kb import show_products_to_user
from keyboards.select_tariffs_kb import get_back_kb_button, action_for_get_paid, action_for_get_paid_2, \
    action_for_get_paid_3
from keyboards.tariffs_kb import tariffs_user_kb, get_tariffs, get_tariffs_for_user
from loader import bot, dp
from states.client_data import FreeCourseState, AllTariffsState
from states.help_state import HelpState
from utils.db import Users, Products, Tariffs
from utils.db.utils import get_user_language
from aiogram.types import InputFile

default_router = Router(name=__name__)


async def send_help_text_to_admin(admin_chat_id, data_to_send):
    """Отправляем данные админу без подтверждения"""
    await bot.send_message(admin_chat_id, data_to_send)


# Создаем функцию для инициализации get_help_text
@sync_to_async
def get_help_text(user_id):
    if user_id not in help_data:
        help_data[user_id] = HelpData()
    return help_data[user_id]


@default_router.message(lambda message: message.text in [uzb_texts['language'], ru_texts['language']])
async def cmd_start(message: types.Message, state: FSMContext, session_maker: sessionmaker, ):
    user_id = message.chat.id
    await state.clear()
    # Запрос выбора языка
    await message.answer("Tilni tanlang:\nВыберите язык:", reply_markup=language_inline)


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session_maker: sessionmaker, ):
    user_id = message.chat.id
    await state.clear()
    if user_id in config.ADMIN_ID:
        await message.answer(ru_texts['answer_for_admin'],
                             reply_markup=admin_kb.markup)
        return
    # Получаем язык пользователя и отправляем соответствующее сообщение
    selected_language = await get_user_language(user_id, session_maker)
    if selected_language:
        await bot.send_photo(user_id,
                             photo=FSInputFile(Image_PATH),
                             caption=_(ru_texts['bot_greeting'], selected_language),
                             reply_markup=await inline_button.action_for_get_info(user_id, session_maker), )
        await message.answer(
            text="👋😃",  # Текст сообщения должен быть непустым, можно использовать пробел
            reply_markup=await default_kb.create_default_markup(user_id, session_maker)
        )
    else:
        # Запрос выбора языка
        await message.answer("Tilni tanlang:\n\nВыберите язык:", reply_markup=language)


# Функция для отправки видео и сообщения
async def send_media_and_message(user_id, media_type=None, media_url=None):
    if media_url is not None:
        if media_type == 'video':
            await bot.send_video(chat_id=user_id, video=media_url)
        elif media_type == 'photo':
            await bot.send_photo(chat_id=user_id, photo=media_url)


COMMANDS = {
    'course_questions': 'course_answer',
    'suitable_for_me': 'suitable_for_me_answer',

    'earn_after_training': 'earn_after_training_answer'
}
relevant_keys = ['course_questions', 'suitable_for_me', 'earn_after_training']
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


@default_router.message(lambda message: message.text in [uzb_texts['about_instar'], ru_texts['about_instar']])
async def cmd_about_instar(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """
    Отправляем информацию о проекте
    :param session_maker:
    :param message:
    :param state:
    :return:
    """
    user_id = message.chat.id
    # Определяем язык пользователя
    user_lang = await get_user_language(user_id, session_maker)
    await message.answer(text=_(ru_texts['about_instar_answer'], user_lang),
                         reply_markup=await about_instar_markup(user_id, session_maker))


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
                         reply_markup=contact_keyboard(user_id))
    await state.set_state(HelpState.contact)


@default_router.message(HelpState.contact)
async def get_contact_from_client(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    admin = config.ADMIN_ID[0]
    user_id = message.chat.id
    help_info = await get_help_text(user_id)
    if message.text:
        help_info.contact = message.text
    else:
        help_info.contact = message.contact.phone_number

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
    lambda message: message.text in [uzb_texts['available_materials'], ru_texts['available_materials']])
async def cmd_get_free_materials(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    keyboard_markup = await show_products_to_user(user_id, session_maker)
    user_lang = await get_user_language(user_id, session_maker)
    await bot.send_message(chat_id=user_id,
                           text=_(ru_texts['bought_course'], user_lang),
                           reply_markup=keyboard_markup)
    await state.set_state(FreeCourseState.course_name)


@default_router.message(FreeCourseState.course_name)
async def process_direction(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.chat.id
    # Используем функцию для инициализации product
    product_name = message.text
    product_info = await Products.get_product_from_name(product_name, session_maker)
    file_id = product_info.file_id
    file_type = product_info.file_type
    description = product_info.description
    if file_id and file_type:
        data = {
            'chat_id': user_id,
            'caption': description,
            file_type: file_id
        }
        att = getattr(bot, f'send_{file_type}')
        await att(**data)
    else:
        await bot.send_message(chat_id=user_id, text=description,
                               reply_markup=await default_kb.create_default_markup(user_id, session_maker))


async def process_tariffs(chat_id: int, state: FSMContext, session_maker: sessionmaker):
    tariffs = await get_tariffs_for_user(session_maker)
    user_lang = await get_user_language(chat_id, session_maker)
    keyboard_markup = await tariffs_user_kb(tariffs, chat_id, session_maker)
    await bot.send_message(chat_id=chat_id,
                           text=_(ru_texts['select_tariff'], user_lang),
                           reply_markup=keyboard_markup)
    await state.set_state(AllTariffsState.tariff_name)


@default_router.callback_query(lambda query: query.data in ['tariffs'])
async def cmd_callback_tariffs(callback_query: types.CallbackQuery, state: FSMContext,
                               session_maker: sessionmaker):
    """Для выбора тарифа из inline клавиатуры"""

    user_id = callback_query.from_user.id
    await process_tariffs(user_id, state, session_maker)


@default_router.message(
    lambda message: message.text in [uzb_texts['tariffs'], ru_texts['tariffs']])
async def cmd_get_tariffs(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    """Для выбора тарифа из обычной клавиатуры"""
    user_id = message.chat.id
    await process_tariffs(user_id, state, session_maker)


@default_router.message(AllTariffsState.tariff_name)
async def cmd_select_tariff(
        message: types.Message,
        state: FSMContext,
        session_maker: sessionmaker
):
    user_id = message.chat.id
    tariff_name, tariff_price_text = message.text.split(" | ")
    user_lang = await get_user_language(user_id, session_maker)
    # переводим с такого вида "3123 UZS" в такой int(3123)
    price = int(tariff_price_text.split()[0])

    tariff: Tariffs = await Tariffs.get_tariff_by_name_and_price(
        tariff_name=tariff_name,
        price=price,
        lang=user_lang, session_maker=session_maker
    )
    # Создаём клавиатуру только с кнопкой "назад" чтобы удалить
    # название тарифов из меню и оставить только кнопку "назад"
    markup = await get_back_kb_button(user_id, session_maker)
    # Этот текст нужно отправить, чтобы удалить кнопки с названием тарифов
    message_details = await message.answer(
        _(ru_texts['paid_details_title'], user_lang),
        reply_markup=markup
    )

    text = _(ru_texts['paid_tariff_name'], user_lang)
    text = text.format(
        tariff_name=await get_tariff_name_by_language(user_lang, tariff),
        tariff_price=tariff.price,
    )
    await message.answer(text, reply_markup=await action_for_get_paid(user_id, session_maker))

    # Сохраняем данные с state, чтобы получить к ним доступ из другого state
    # передаём туда также id побочного текста которой мы использовали для изменения
    # меню, чтобы иметь возможность его удалить
    await state.set_data(
        {
            'tariff_id': tariff.id,
            'prev_states': [AllTariffsState.tariff_name],
            'message_details_id': message_details.message_id
        }
    )

    await state.set_state(AllTariffsState.paid_details)


@default_router.callback_query(AllTariffsState.paid_details, F.data == 'paid_tariff')
async def tariff_paid_details(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        session_maker: sessionmaker
):
    await callback_query.answer()

    await update_state(state)

    data = await state.get_data()
    user_id = callback_query.message.chat.id
    user_lang = await get_user_language(user_id, session_maker)
    tariff: Tariffs = await Tariffs.get_tariff_by_id(
        tariff_id=data['tariff_id'], session_maker=session_maker
    )

    text = _(ru_texts['paid_transfer_details'], user_lang)
    text = text.format(
        tariff_name=await get_tariff_name_by_language(user_lang, tariff)
    )

    await callback_query.message.edit_text(
        text, reply_markup=await action_for_get_paid_2(user_id, session_maker)
    )

    await state.set_state(AllTariffsState.paid_action)


@default_router.callback_query(AllTariffsState.paid_action, F.data == 'paid_action')
async def tariff_paid_action(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        session_maker: sessionmaker
):
    await callback_query.answer()

    data = await state.get_data()
    user_id = callback_query.message.chat.id
    user_lang = await get_user_language(user_id, session_maker)
    tariff: Tariffs = await Tariffs.get_tariff_by_id(
        tariff_id=data['tariff_id'], session_maker=session_maker
    )

    text = _(ru_texts['paid_total'], user_lang)
    text = text.format(
        tariff_name=await get_tariff_name_by_language(user_lang, tariff),
        tariff_price=tariff.price
    )

    await update_state(state)
    await callback_query.message.edit_text(
        text,
        reply_markup=await action_for_get_paid_3(user_id, session_maker)
    )
    await state.set_state(AllTariffsState.paid_check)


@default_router.message(AllTariffsState.paid_check, (F.photo | F.document | F.video))
async def paid_photo_check(
        message: types.Message,
        state: FSMContext,
        session_maker: sessionmaker
):
    data = await state.get_data()
    tariff = await Tariffs.get_tariff_by_id(data['tariff_id'], session_maker)
    user: Users = await Users.get_user_by_id(message.chat.id, session_maker)
    user_lang = await get_user_language(message.chat.id, session_maker)

    text = _(ru_texts['paid_admin_check'], user_lang)
    text = text.format(
        user_id=message.from_user.id,
        user_name=message.from_user.username or message.from_user.first_name,
        phone=user.phone,
        tariff_name=await get_tariff_name_by_language(user_lang, tariff),
        tariff_price=tariff.price
    )
    markup = await get_payment_confirm_reject_markup(
        user_id=message.from_user.id,
        tariff_id=tariff.id,
        session_maker=session_maker
    )
    if message.content_type == 'photo':
        await bot.send_photo(
            chat_id=config.ADMIN_ID[0],
            caption=text,
            photo=message.photo[-1].file_id,
            reply_markup=markup
        )
    if message.content_type == 'document':
        await bot.send_document(
            chat_id=config.ADMIN_ID[0],
            caption=text,
            document=message.document.file_id,
            reply_markup=markup
        )
    await message.answer(
        _(ru_texts['paid_success_send'], user_lang),
        reply_markup=await default_kb.create_default_markup(message.chat.id, session_maker)
    )
    await state.clear()


@default_router.callback_query(F.data == 'prev_action')
async def tariff_prev_button(
        callback_query: types.CallbackQuery,
        state: FSMContext,
        session_maker: sessionmaker
):
    await callback_query.answer()

    user_id = callback_query.message.chat.id
    user_lang = await get_user_language(user_id, session_maker)
    data = await state.get_data()
    prev_states = data.get('prev_states', [])

    # При нажатии inline кнопки "назад" предыдущий state
    # и устанавливаем его как текущий.
    prev_state = prev_states.pop()
    await state.set_state(prev_state)

    tariff_id = data.get('tariff_id')
    tariff = await Tariffs.get_tariff_by_id(
        tariff_id=int(tariff_id), session_maker=session_maker
    )

    # В зависимости каким был предыдущий state заново формируем для него текст
    if prev_state == AllTariffsState.tariff_name:
        tariffs = await get_tariffs(session_maker)
        keyboard_markup = await tariffs_user_kb(tariffs, user_id, session_maker)

        # Чтобы заново отправить меню с названиями тарифов нам нужно сначала
        # удалить текст с inline кнопками и потом отправить новое сообщение
        # с нашим меню. И ещё заодно удаляем побочный текст.
        await callback_query.message.delete()
        await bot.delete_message(user_id, message_id=data.pop('message_details_id'))
        await callback_query.message.answer(
            _(ru_texts['choose_tariffs'], user_lang),
            reply_markup=keyboard_markup
        )
        return

    if prev_state == AllTariffsState.paid_details:
        text = _(ru_texts['paid_tariff_name'], user_lang)
        text = text.format(
            tariff_name=await get_tariff_name_by_language(user_lang, tariff),
            tariff_price=tariff.price,
        )
        await callback_query.message.edit_text(
            text, reply_markup=await action_for_get_paid(user_id, session_maker)
        )
        return

    if prev_state == AllTariffsState.paid_action:
        text = _(ru_texts['paid_transfer_details'], user_lang)
        text = text.format(
            tariff_name=await get_tariff_name_by_language(user_lang, tariff)
        )
        await callback_query.message.edit_text(
            text, reply_markup=await action_for_get_paid_2(user_id, session_maker)
        )


@default_router.callback_query(
    PayConfirmCallback.filter(
        (F.action == PayConfirmAction.CONFIRM) |
        (F.action == PayConfirmAction.REJECT)
    )
)
async def paid_confirm_reject(
        callback_query: types.CallbackQuery,
        callback_data: CallbackData,
        session_maker: sessionmaker
):
    user_lang = await get_user_language(callback_query.message.chat.id, session_maker)
    alert_text = None
    if callback_data.action == PayConfirmAction.CONFIRM:
        user: Users = await Users.get_user_by_id(callback_data.user_id, session_maker)
        if user.tariff_id == callback_data.tariff_id:
            alert_text = _(ru_texts['paid_admin_already_confirm'], user_lang)

        if user.tariff_id != callback_data.tariff_id:
            alert_text = _(ru_texts['paid_admin_tariff_update'], user_lang)

        if not user.tariff_id:
            alert_text = _(ru_texts['paid_admin_confirm'], user_lang)

        if user.tariff_id != callback_data.tariff_id:
            await Users.update_user(
                user_id=user.user_id,
                session_maker=session_maker,
                tariff_id=callback_data.tariff_id
            )

    if callback_data.action == PayConfirmAction.REJECT:
        alert_text = _(ru_texts['paid_admin_reject'], user_lang)

    await callback_query.message.edit_caption(
        caption=f'{callback_query.message.caption} \n {alert_text}'
    )
    await callback_query.answer(alert_text, show_alert=True)
    user_send_text = _(ru_texts['paid_user_send_text'], user_lang)
    user_send_text = user_send_text.format(alert_text=alert_text)
    await bot.send_message(callback_data.user_id, user_send_text)


async def update_state(state: FSMContext):
    # Получаем данные из предыдущего state и обновляем их новыми данными.
    # Prev_states записываем, чтобы inline кнопка назад работало.
    data = await state.get_data()
    data['prev_states'].append(await state.get_state())
    await state.set_data(data)


async def get_tariff_name_by_language(user_lang: str, tariff: Tariffs):
    if user_lang == 'uzb':
        return tariff.tariff_name_uzb
    return tariff.tariff_name


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


async def send_large_file_from_google_drive(chat_id: int, file_url: str, ):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                # Для больших файлов лучше сохранять файл на диск,
                # а не держать его в памяти
                with open('tempfile', 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)  # Читаем по кусочкам
                        if not chunk:
                            break
                        file.write(chunk)
                with open('tempfile', 'rb') as file:
                    await bot.send_document(chat_id, document=file)
            else:
                await bot.send_message(chat_id, "Не удалось скачать файл.")
