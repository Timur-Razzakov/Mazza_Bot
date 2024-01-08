from aiogram.fsm.state import StatesGroup, State


# Машина состояний для отправки данных
class ClientDataState(StatesGroup):
    user_name = State()
    user_number = State()


class FreeCourseState(StatesGroup):
    course_name = State()


class AllTariffsState(StatesGroup):
    tariff_name = State()
    paid_details = State()
    paid_action = State()
    paid_check = State()