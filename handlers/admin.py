from aiogram import types, Router, F
from aiogram.types import FSInputFile
from openpyxl.workbook import Workbook
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import ru_texts
from keyboards import default_kb
from utils.db import Users

admin_router = Router(name=__name__)
# используется для определения какие действия будут после выбора страны
current_state = 'admin_data'


@admin_router.message(F.text == ru_texts['home'])
async def cmd_home(message: types.Message, session_maker: sessionmaker, ):
    user_id = message.chat.id

    if user_id in config.ADMIN_ID:
        await message.answer("Вы успешно перешли в главное меню!",
                             reply_markup=await default_kb.create_default_markup(user_id, session_maker))
    else:
        await message.answer(ru_texts['admin_no_access'])


# @dp.callback_query(
#     SendAdmin.filter(
#         (F.status == SendAdminStatus.CONFIRM) | (F.status == SendAdminStatus.REJECT)
#     )
# )
# # Слушаем ответ админа и отправляем клиенту
# async def send_to_client(
#         callback_query: types.CallbackQuery,
#         callback_data: CallbackData,
#         state: FSMContext
# ):
#     user_id = callback_query.message.chat.id
#     text = callback_query.message.text
#     data_dict_user_id = callback_data.user_id
#     selected_language = user_language.get(data_dict_user_id,
#                                           "ru")  # По умолчанию, если язык не задан, используем 'ru'
#     if callback_data.status == SendAdminStatus.REJECT:
#         # удаляем сообщение с кнопкой, для избежания повторного нажатия
#         await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
#         await bot.send_message(data_dict_user_id, text=_(ru_texts['application_rejected'], selected_language))
#         await bot.send_message(user_id, text=ru_texts['user_notified'])
#     elif callback_data.status == SendAdminStatus.CONFIRM:
#         # удаляем сообщение с кнопкой, для избежания повторного нажатия
#         await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
#         await bot.send_message(data_dict_user_id,
#                                text=_(ru_texts['application_approved'], selected_language))
#         await bot.send_message(user_id, text=text)
#     await state.clear()

@admin_router.message(F.text == ru_texts['download_excel'])
async def download_excel(message: types.Message, session_maker):
    user_id = message.chat.id
    if user_id not in config.ADMIN_ID:
        await message.answer(ru_texts['admin_no_access'])
        return

    users_tariffs = await Users.get_all_users_tariffs(session_maker)

    wb = Workbook()
    sh1 = wb.active
    sh1.title = 'Report'
    sh1.append(('№', 'User ID', 'Имя', 'Номер телефона', 'Язык', 'Тариф', 'Дата регистрации'))
    user_number = 0
    for user, tariff in users_tariffs:
        user_number += 1
        sh1.append(
            (user_number,
             user.user_id, user.name, user.phone, user.lang,
             tariff.tariff_name if tariff else 'Отсутствует',
             user.created_at
             )
        )

    wb.save('report.xlsx')
    file = FSInputFile('report.xlsx')
    await message.answer_document(file)
