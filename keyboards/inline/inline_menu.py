from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

menu_categories = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Отклонить", callback_data="admin_card_reject"),
            InlineKeyboardButton("Подтвердить", callback_data="admin_card_approve")
        ]
    ],
    one_time_keyboard=True
)
