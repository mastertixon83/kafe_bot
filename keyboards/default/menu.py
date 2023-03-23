from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menuUser = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏚 О ресторане"),
            KeyboardButton(text="👍 Отзывы"),
        ],
        [
            KeyboardButton(text="📋 Меню")
        ],
        [
            KeyboardButton(text="🔔 Вызов персонала"),
            KeyboardButton(text="🍽 Забронировать стол"),
        ],
        [
            KeyboardButton(text="🚚 Оформить заказ на доставку")
        ],
        [
            KeyboardButton(text="👍 Программа лояльности"),
            KeyboardButton(text="🚶 Пригласить друга")
        ],
        [
            KeyboardButton(text="❓ Задайте нам вопрос")
        ],
    ],
    resize_keyboard=True
)

menuAdmin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏚 О ресторане"),
            KeyboardButton(text="👍 Отзывы"),
        ],
        [
            KeyboardButton(text="📋 Меню"),
        ],
        [
            KeyboardButton(text="🔔 Вызов персонала"),
            KeyboardButton(text="🍽 Забронировать стол")
        ],
        [
            KeyboardButton(text="🚚 Оформить заказ на доставку")
        ],
        [
            KeyboardButton(text="💳 Программа лояльности"),
            KeyboardButton(text="🚶 Пригласить друга")
        ],
        [
            KeyboardButton(text="📩 Сделать рассылку подписчикам")
        ],
        [
            KeyboardButton(text="⚙️ Настройки"),
            KeyboardButton(text="📊 Аналитика")

        ],
    ],
    resize_keyboard=True
)

menuPersonal = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👦 Официант")
        ],
        [
            KeyboardButton(text="👲 Кальянный мастер")
        ],
        [
            KeyboardButton(text="⬅ Главное меню")
        ],
    ],
    resize_keyboard=True
)

menuLoyality = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("💳 Оформить карту")],
        [KeyboardButton("🎁 Мои подарки")],
        [KeyboardButton("⬅ Главное меню")]
    ],
    resize_keyboard=True
)

cancel_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("⬅ Главное меню")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

send_phone_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📲 Отправить свой контакт", request_contact=True)],
        [KeyboardButton("⬅ Главное меню")]
    ],
    resize_keyboard=True
)

send_phone = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📲 Отправить свой контакт", request_contact=True)]
    ],
    resize_keyboard=True
)

menu_admin_config = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Администраторы бота")],
        [
            KeyboardButton("Список нарушителей")
        ],
        [KeyboardButton('Отключить все активные рассылки')],
        [KeyboardButton("Редактировать меню")],
        [KeyboardButton("Редактировать отзывы")],
        [KeyboardButton("⬅ Главное меню")]
    ]
)

newsletter_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📨 Обычная рассылка")],
        # [KeyboardButton("📝 Анкетирование (Опрос)")],
        [KeyboardButton("🎁 Предложение для именинников")],
        [KeyboardButton("🍽 Призыв к бронированию")],
        [KeyboardButton("🚚 Закажите доставку")],
        [KeyboardButton("💳 Владельцам карт лояльности")],
        # [KeyboardButton("👥 Группе пользователей")],
        # [KeyboardButton("👤 Конкретным пользователям")],
        [KeyboardButton("⬅ Главное меню")]
    ]
)

analytics_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Пользователи")],
        [KeyboardButton("Рассылки")],
        [KeyboardButton("Статистика вызовова персонала")],
        [KeyboardButton("Статистика бронирований")],
        [KeyboardButton("Статистика доставки")],
        [KeyboardButton("Участники программы лояльности")],
        [KeyboardButton("⬅ Главное меню")]
    ]
)
