import json
import os

# Определение пути к корневой папке проекта
project_root = os.path.dirname(os.path.abspath(__file__))

# Построение пути к файлу ru.json
path_to_ru_json = os.path.join(project_root, 'ru.json')
path_to_uzb_json = os.path.join(project_root, 'uzb.json')
# Загрузка текста
with open(path_to_ru_json, 'r', encoding='utf-8') as file:
    ru_texts = json.load(file)

with open(path_to_uzb_json, 'r', encoding='utf-8') as file:
    uzb_texts = json.load(file)

translations = {
    'uzb': {}
}
# объединяем слова
for key in ru_texts:
    translations['uzb'][ru_texts[key]] = uzb_texts[key]


def _(text, lang):
    """Функция, для определения какой текст нужно возвращать uzb или ru"""
    if lang == 'ru':
        return text
    else:
        global translations
        try:
            return translations[lang][text]
        except Exception:
            return text


# вынес сюда, так как были проблемы с импортами

user_language = {}  # Пример: {'user_id': 'ru'}

# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
#
# def generate_markup(user_language):
#     if user_language == 'uz':
#         translations = translations_uz
#     else:  # default language
#         translations = {
#             'Выкуп': 'Выкуп',
#             'Помощь ⭐️': 'Помощь ⭐️',
#             # ... остальные переводы
#         }
#
#     return ReplyKeyboardMarkup(
#         keyboard=[
#             [
#                 KeyboardButton(text=translations['Выкуп']),
#                 KeyboardButton(text=translations['Помощь ⭐️']),
#                 KeyboardButton(text=translations['Запрещённые товары 🚫️']),
#             ],
#             [
#                 KeyboardButton(text=translations['Получить персональный адрес 📌']),
#             ],
#             [
#                 KeyboardButton(text=translations['Оформить заказ⏱']),
#             ],
#         ],
#         resize_keyboard=True
#     )
