import os
from datetime import datetime

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from sqlalchemy.orm import sessionmaker

from data import config
from data.data_classes import courses_data, CourseData
from data.translations import ru_texts
from keyboards import admin_kb
from keyboards.inline_button import action_for_select_free_course_or_not
from keyboards.products_kb import products_kb, get_products, update_product_kb
from keyboards.tariffs_kb import tariffs_kb, get_tariffs
from loader import bot
from states.course_state import CourseState, AddCourseState
from utils.db import Products, Tariffs

course_router = Router(name=__name__)




# Создаем функцию для инициализации get_course_data
@sync_to_async
def get_course_data(user_id):
    if user_id not in courses_data:
        courses_data[user_id] = CourseData()
    return courses_data[user_id]


@course_router.message(F.text == ru_texts['add_course'])
async def cmd_add_course(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        await message.answer(ru_texts['product_name'],
                             reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddCourseState.product_name)
    else:
        await message.answer(ru_texts['admin_no_access'])


@course_router.message(AddCourseState.product_name)
async def get_product_name(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    product_name = message.text.upper()
    if user_id in config.ADMIN_ID:
        # Проверяем есть ли в бд такой курс
        product_id = await get_product_id(product_name, session_maker)
        if product_id is None:
            product = await get_course_data(user_id)
            product.user_id = user_id
            product.product_name = product_name
            await message.answer(ru_texts['product_name_uzb'],
                                 reply_markup=admin_kb.cancel_markup)
            await state.set_state(AddCourseState.product_name_uzb)
        else:
            await message.answer(ru_texts['already_exists'],
                                 reply_markup=admin_kb.markup)
            await state.clear()
            return
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@course_router.message(AddCourseState.product_name_uzb)
async def get_product_name_uzb(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    product_name_uzb = message.text.upper()
    if user_id in config.ADMIN_ID:
        product = await get_course_data(user_id)
        product.user_id = user_id
        product.product_name_uzb = product_name_uzb
        await message.answer(ru_texts['course_is_free'],
                             reply_markup=await action_for_select_free_course_or_not(user_id, session_maker))
        await state.set_state(AddCourseState.free)
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@course_router.message(AddCourseState.free)
@course_router.callback_query(lambda query: query.data in ['yes', 'no'])
async def get_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.message.chat.id
    await callback_query.answer()
    product = await get_course_data(user_id)
    if callback_query.data == 'yes':
        product.is_free = True
    elif callback_query.data == 'no':
        product.is_free = False
    await bot.send_message(user_id, ru_texts['product_description'],
                           reply_markup=admin_kb.cancel_markup)
    await state.set_state(AddCourseState.description)


@course_router.message(AddCourseState.description)
async def get_product_description(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        product = await get_course_data(user_id)
        product.description = message.text
        await bot.send_message(chat_id=user_id,
                               text=ru_texts['description_uzb'],
                               reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddCourseState.description_uzb)
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@course_router.message(AddCourseState.description_uzb)
async def get_product_description_uzb(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        product = await get_course_data(user_id)
        product.description_uzb = message.text
        await bot.send_message(chat_id=user_id,
                               text=ru_texts['download_file'],
                               reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddCourseState.file_id)
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@course_router.message(AddCourseState.file_id, (F.Text | F.photo | F.document | F.video))
async def get_product_description(message: types.Message,
                                  session_maker: sessionmaker,
                                  state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        product = await get_course_data(user_id)
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
        elif message.content_type == 'video':
            file_id = message.video.file_id
        elif message.content_type == 'document':
            file_id = message.document.file_id
        else:  # Для документов
            file_id = None

        product.file_id = file_id
        product.file_type = message.content_type
        await message.reply("Файл сохранен!")
        # Получаем список тарифов
        tariffs = await get_tariffs(session_maker)
        # Вызываем функцию tariffs_kb, чтобы получить список тарифов и клавиатурный markup
        keyboard_markup = await tariffs_kb(tariffs, user_id, session_maker)
        await bot.send_message(chat_id=user_id,
                               text=ru_texts['select_tariff'],
                               reply_markup=keyboard_markup)
        await state.set_state(AddCourseState.tariff_id)
    else:
        await message.answer(ru_texts['admin_no_access'])
        await state.clear()


@course_router.message(AddCourseState.tariff_id)
async def process_get_tariff_id(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.chat.id
    # Используем функцию для инициализации user_order
    product = await get_course_data(user_id)
    tariff_name = message.text
    tariff_info = await Tariffs.get_tariff_from_name(tariff_name, session_maker)
    product.tariff_id = tariff_info.id
    if product.product_id is not None:
        update_fields = {
            "product_name": str(product.product_name),
            "product_name_uzb": str(product.product_name_uzb),
            "free": product.is_free,
            "file_id": product.file_id,
            "file_type": product.file_type,
            "description": str(product.description),
            "description_uzb": str(product.description_uzb),
            "tariff_id": int(product.tariff_id),
        }
        await update_product(product_id=product.product_id,
                             session_maker=session_maker,
                             **update_fields)
        # После завершения использования, создаём новый экземпляр для очистки старого
        product.reset()
        text_for_message = ru_texts['data_updated']
    else:
        await save_product(product_name=str(product.product_name),
                           product_name_uzb=str(product.product_name_uzb),
                           description=str(product.description),
                           description_uzb=str(product.description_uzb),
                           tariff_id=int(product.tariff_id),
                           free=product.is_free,
                           file_id=product.file_id,
                           file_type=product.file_type,
                           session_maker=session_maker)
        product.reset()
        text_for_message = ru_texts['saved_thank_you']
    await state.clear()  # очищаем state
    await message.answer(text_for_message, reply_markup=admin_kb.markup)


@course_router.message(F.text == ru_texts['all_courses'])
async def cmd_all_courses(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user_id = message.chat.id
    if user_id in config.ADMIN_ID:
        # Получаем список курсов
        courses = await get_products(session_maker)
        # Вызываем функцию country_kb, чтобы получить список стран и клавиатурный markup
        keyboard_markup = await products_kb(courses, user_id, session_maker)
        await state.set_state(CourseState.product_name)
        await bot.send_message(chat_id=user_id,
                               text=ru_texts['choose_courses'],
                               reply_markup=keyboard_markup)
    else:
        await message.answer(ru_texts['admin_no_access'])


@course_router.message(CourseState.product_name)
async def process_product_name(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.chat.id
    # Используем функцию для инициализации user_order
    product = await get_course_data(user_id)
    product_name = message.text
    product_info = await Products.get_product_from_name(product_name, session_maker)
    product.product_id = product_info.id
    if product_name == ru_texts['back']:
        await message.answer(ru_texts['goodbye'], reply_markup=admin_kb.markup)
        await state.clear()
        # После завершения использования, создаём новый экземпляр для очистки старого
        product.reset()
        return
    else:
        tariff_id = product_info.tariff_id
        product.tariff_id = tariff_id
        if tariff_id is not None:
            get_tariff_name = await Tariffs.get_tariff(product_info.tariff_id, session_maker)
        else:
            get_tariff_name = tariff_id
        text = await text_for_product_info(product_name=product_info.product_name,
                                           product_name_uzb=product_info.product_name_uzb,
                                           free=product_info.free,
                                           file_id=product_info.file_id,
                                           file_type=product_info.file_type,
                                           tariff_name=get_tariff_name,
                                           description=product_info.description,
                                           description_uzb=product_info.description_uzb)
        await message.answer(text, reply_markup=update_product_kb(user_id))
        return


@course_router.callback_query(lambda query: query.data in ['update_product', 'delete_product'])
async def update_or_delete_product(callback_query: types.CallbackQuery, session_maker: sessionmaker,
                                   state: FSMContext):
    await callback_query.answer()
    """Функция для обновления доставки"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    product = await get_course_data(user_id)
    if data == 'delete_product':
        await del_product(product.product_id, session_maker)
        await bot.send_message(user_id, ru_texts['product_deleted'], reply_markup=admin_kb.markup)
        await state.clear()
    elif data == 'update_product':
        await bot.send_message(user_id, ru_texts['product_name'],
                               reply_markup=admin_kb.cancel_markup)
        await state.set_state(AddCourseState.product_name)
    # удаляем сообщение с кнопкой, для избежания повторного нажатия
    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)


@sync_to_async
def text_for_product_info(tariff_name, description, description_uzb, free, file_id, file_type, product_name,
                          product_name_uzb):
    # собираем в таблицу для админа
    message_text = ''
    message_text += "<pre>"
    message_text += "{:<15} : {:<15}\n".format("Tariff name",
                                               tariff_name if tariff_name is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("Course is Free", "бесплатно" if free else "платно")
    message_text += "{:<15} : {:<15}\n".format("File_id", file_id if file_id is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("File_type", file_type if file_type is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("Course name ", product_name)
    message_text += "{:<15} : {:<15}\n".format("Course name(UZB)",
                                               product_name_uzb if product_name_uzb is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("Description",
                                               description[:300] + '...' if description is not None else "N/A")
    message_text += "{:<15} : {:<15}\n".format("Description(UZB)",
                                               description_uzb[:300] + '...' if description_uzb is not None else "N/A")
    message_text += "</pre>"
    return message_text


async def get_product_id(product_name, session_maker):
    product_id = await Products.get_product_from_name(product_name=product_name, session_maker=session_maker)
    return product_id


async def save_product(product_name, product_name_uzb, tariff_id, description,
                       description_uzb, file_id,file_type, free, session_maker):
    product = await Products.create_product(
        product_name=product_name,
        product_name_uzb=product_name_uzb,
        description_uzb=description_uzb,
        description=description,
        tariff_id=tariff_id,
        free=free,
        file_id=file_id,
        file_type=file_type,
        session_maker=session_maker)
    return product


async def del_product(product_id, session_maker):
    """
    Удаляем курс
    :param product_id:
    :param session_maker:
    :return:
    """
    product = await Products.delete_product_by_id(product_id, session_maker)
    return product


async def update_product(product_id, session_maker, **update_fields):
    """
       Асинхронно обновляет информацию о конкретном продукте.

       :param product_id: ID продукта, который нужно обновить.
       :param session_maker: Фабрика сессий SQLAlchemy.
       :param update_fields: Ключевые аргументы, представляющие поля для обновления и их новые значения.
       :return: Обновленный объект продукта или None, если продукт не существует."""

    updated_product = await Products.update_product(
        product_id=product_id,
        session_maker=session_maker,
        **update_fields
    )
    return updated_product
