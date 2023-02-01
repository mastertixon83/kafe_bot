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

hall_reservation_inline_count_mans = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("1", callback_data="person-1"),
            InlineKeyboardButton("2", callback_data="person-2")
        ],
        [
            InlineKeyboardButton("3", callback_data="person-3"),
            InlineKeyboardButton("4", callback_data="person-4")
        ],
        [
            InlineKeyboardButton("5", callback_data="person-5"),
            InlineKeyboardButton("6", callback_data="person-6")
        ],
        [
            InlineKeyboardButton("10", callback_data="person-10")
        ],
    ]
)

admin_inline_hall_edit = InlineKeyboardMarkup(
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
            InlineKeyboardButton("Отменить бронь", callback_data="reject_order"),
            InlineKeyboardButton("Назад", callback_data="go_back"),

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
