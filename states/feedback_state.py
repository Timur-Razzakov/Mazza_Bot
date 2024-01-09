from aiogram.fsm.state import StatesGroup, State


# Машина состояний для ссылки на товар
class FeedbackState(StatesGroup):
    """Для сообщения от пользователя админу"""
    feedback = State()
