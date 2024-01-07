from aiogram.fsm.state import StatesGroup, State


class AddCourseState(StatesGroup):
    product_name = State()
    product_name_uzb = State()
    description = State()
    description_uzb = State()
    tariff_id = State()
    free = State()
    url = State()


class CourseState(StatesGroup):
    product_name = State()
    product_name_uzb = State()
    description = State()
    description_uzb = State()
    tariff_id = State()
    free = State()
    url = State()


class DelCourseState(StatesGroup):
    product_name = State()


class UpdateCourseState(StatesGroup):
    product_name = State()
