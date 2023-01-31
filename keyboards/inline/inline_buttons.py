from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove


admin_card_approve = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Отклонить", callback_data="admin_card_reject"),
            InlineKeyboardButton("Подтвердить", callback_data="admin_card_approve")
        ]
    ],
    one_time_keyboard=True
)


admin_inline_staff = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Стол N1", callback_data="user_id-approved-1-free"),
            InlineKeyboardButton("Стол N2", callback_data="user_id-approved-2-free"),
            InlineKeyboardButton("Стол N3", callback_data="user_id-approved-3-free")
        ],
        [
            InlineKeyboardButton("Стол N4", callback_data="user_id-approved-4-free"),
            InlineKeyboardButton("Стол N5", callback_data="user_id-approved-5-free"),
            InlineKeyboardButton("Стол N6", callback_data="user_id-approved-6-free")
        ],
        [
            InlineKeyboardButton("Отклонить", callback_data="user_id-rejected"),
            # InlineKeyboardButton("Подтвердить", callback_data="user_id-approved")
        ],
        [
            InlineKeyboardButton("Зал заполнен", callback_data="user_id-foolrest")
        ],
        [
            InlineKeyboardButton("Написать гостю в ЛС", callback_data="user_id:send_ls", url=f"https://t.me/")
        ]
    ]
)

user_inline_approve = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Подтвердить", callback_data="approve_order_user"),
            InlineKeyboardButton("Отмена", callback_data="cancel_order_user")
        ]
    ]
)

get_prize_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Получить подарок", callback_data="get_prize")
        ]
    ]
)

admin_inline_send_ls = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Написать гостю в ЛС", callback_data="write_to_pm", url=f"https://t.me/")
        ]
    ]
)