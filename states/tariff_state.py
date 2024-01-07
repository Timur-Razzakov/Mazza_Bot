from aiogram.fsm.state import StatesGroup, State


class AddTariffState(StatesGroup):
    tariffs_name = State()
    description = State()
    price = State()


class TariffState(StatesGroup):
    tariffs_name = State()
    description = State()
    price = State()


class DelTariffState(StatesGroup):
    tariffs_name = State()


class UpdateTariffState(StatesGroup):
    tariffs_name = State()
