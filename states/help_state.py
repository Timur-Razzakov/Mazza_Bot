from aiogram.fsm.state import StatesGroup, State


# Машина состояний для ссылки на товар
class HelpState(StatesGroup):
    """Для сообщения от пользователя админу"""
    text = State()
    contact = State()
