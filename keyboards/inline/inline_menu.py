from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_categories = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Отклонить", callback_data="admin_card_reject"),
            InlineKeyboardButton("Подтвердить", callback_data="admin_card_approve")
        ]
    ],
    one_time_keyboard=True
)
