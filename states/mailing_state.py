from aiogram.fsm.state import StatesGroup, State


# Машина состояний для ссылки на рассылки
class MailingState(StatesGroup):
    message_for_client = State()
    lang = State()
