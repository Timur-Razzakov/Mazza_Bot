import enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import sessionmaker

from data import config
from data.translations import ru_texts, _
from handlers.click_cancel_or_back import get_user_language


class PayConfirmAction(enum.Enum):
    CONFIRM = 'CONFIRM'
    REJECT = 'REJECT'


class PayConfirmCallback(CallbackData, prefix='pay_confirm'):
    action: PayConfirmAction
    user_id: int
    tariff_id: int


async def get_payment_confirm_reject_markup(
        user_id: int,
        tariff_id: int,
        session_maker: sessionmaker

):
    user_lang = await get_user_language(config.ADMIN_ID[0], session_maker)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_(ru_texts['paid_admin_confirm_btn'], user_lang),
                    callback_data=PayConfirmCallback(
                        action=PayConfirmAction.CONFIRM,
                        user_id=user_id,
                        tariff_id=tariff_id
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=_(ru_texts['paid_admin_reject_btn'], user_lang),
                    callback_data=PayConfirmCallback(
                        action=PayConfirmAction.REJECT,
                        user_id=user_id,
                        tariff_id=tariff_id
                    ).pack()
                ),
            ]
        ], resize_keyboard=True, one_time=True
    )
