from aiogram.fsm.state import StatesGroup, State


class AddTariffState(StatesGroup):
    tariff_name = State()
    tariff_name_uzb = State()
    description = State()
    description_uzb = State()
    price = State()


class TariffState(StatesGroup):
    tariff_name = State()
    tariff_name_uzb = State()
    description = State()
    description_uzb = State()
    price = State()


class DelTariffState(StatesGroup):
    tariff_name = State()


class UpdateTariffState(StatesGroup):
    tariff_name = State()
