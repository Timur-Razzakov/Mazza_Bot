import asyncio

from loader import bot
from utils.db import Users, Products


async def get_user_language(user_id, session_maker):
    user = await Users.get_user(user_id=user_id,
                                session_maker=session_maker)
    return user


async def delayed_message(product_name, user_id, session_maker, user_lang, delay, markup, message, ):
    """Функция для ожидания отправки сообщения"""
    await asyncio.sleep(delay)
    await send_product_info(product_name=product_name, user_lang=user_lang, user_id=user_id,
                            session_maker=session_maker,
                            markup=markup, message=message)


async def send_product_info(product_name, user_lang, user_id, session_maker, markup, message):
    """Функция для отправки различных видео/файлов/фото и если нет, то просто текст"""
    if product_name is None:
        await bot.send_message(user_id, message, reply_markup=markup)
    product_info = await Products.get_product_from_name(product_name, session_maker)
    if product_info is None:
        await bot.send_message(
            chat_id=user_id,
            text="Бесплатный урок временно отсутствует!!",
        )
        return
    file_id = product_info.file_id
    file_type = product_info.file_type
    data = {
        'ru': 'description',
        'uzb': 'description_uzb'
    }
    description = getattr(product_info, data.get(user_lang))

    if file_id and file_type:
        data = {
            'chat_id': user_id,
            'caption': description,
            file_type: file_id,
            'reply_markup': markup
        }
        att = getattr(bot, f'send_{file_type}')
        await att(**data)
    else:
        # Если информация о файле отсутствует, отправляем только текстовое сообщение
        await bot.send_message(
            chat_id=user_id,
            text=description,
            reply_markup=markup
        )
