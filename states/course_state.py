from aiogram.fsm.state import StatesGroup, State


class AddCourseState(StatesGroup):
    product_name = State()
    description = State()
    tariff_id = State()
    free = State()


class CourseState(StatesGroup):
    product_name = State()
    description = State()
    tariff_id = State()
    free = State()


class DelCourseState(StatesGroup):
    product_name = State()


class UpdateCourseState(StatesGroup):
    product_name = State()
