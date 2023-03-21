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
        [InlineKeyboardButton("🎓 Я студент", callback_data="uw_student")],
        [InlineKeyboardButton("💰 Я предприниматель", callback_data="uw_busines")],
        [InlineKeyboardButton("💼 Работаю в найме", callback_data="uw_employee")],
        [InlineKeyboardButton("💻 Фрилансер", callback_data="uw_freelancer")]

    ],
    one_time_keyboard=True
)