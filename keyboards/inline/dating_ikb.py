from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_gender_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Я девушка 🙍‍♀", callback_data="ug_female")],
        [InlineKeyboardButton("Я парень 🙍‍♂️", callback_data="ug_male")]
    ],
    one_time_keyboard=True
)

user_work_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("20-30", callback_data="20-30")],
        [InlineKeyboardButton("30-40", callback_data="30-40")],
        [InlineKeyboardButton("40-50", callback_data="40-50")],
        [InlineKeyboardButton("50+", callback_data="50+")]

    ],
    one_time_keyboard=True
)