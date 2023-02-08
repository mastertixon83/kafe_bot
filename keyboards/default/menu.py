from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menuUser = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="О нас"),
        ],
        [
            KeyboardButton(text="Меню")
        ],
        [
            KeyboardButton(text="Вызов персонала"),
            KeyboardButton(text="Забронировать стол")
        ],
        [
            KeyboardButton(text="Доставка")
        ],
        [
            KeyboardButton(text="Программа лояльности"),
            KeyboardButton(text="Пригласить друга")
        ],
        [
            KeyboardButton(text="Проложить маршрут")
        ],
        [
            KeyboardButton(text="Написать владельцу")
        ],
        [
            KeyboardButton(text="Сделать рассылку подписчикам")
        ],
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Аналитика")

        ],
    ],
    resize_keyboard=True
)


menuAdmin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Ты гребаный Администратор")
        ],
        [
            KeyboardButton(text="Заявки")
        ],
        [
            KeyboardButton(text="Доставка")
        ],
        [
            KeyboardButton(text="Программа лояльности"),
            KeyboardButton(text="Пригласить друга")
        ],
        [
            KeyboardButton(text="Проложить маршрут")
        ],
        [
            KeyboardButton(text="Написать владельцу")
        ],
        [
            KeyboardButton(text="Сделать рассылку подписчикам")
        ],
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Аналитика")

        ],
    ],
    resize_keyboard=True
)


menuAdminOrders = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Все заявки")
        ],
        [
            KeyboardButton(text="Бронирование")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)


menuPersonal = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Официант")
        ],
        [
            KeyboardButton(text="Кальянный мастер")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)

menuLoyality = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Получить карту")],
        [KeyboardButton("Мои коды")],
        [KeyboardButton("Назад")]
    ],
    resize_keyboard=True
)

cancel_btn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

send_phone_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Отправить свой контакт", request_contact=True)],
        [KeyboardButton("Назад")]
    ],
    resize_keyboard=True
)

menu_admin_config = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Администраторы бота")],
        [
            KeyboardButton("Предупредить"),
            KeyboardButton("Заблокировать")
        ],
        [KeyboardButton("Разблокировать пользователя")],
        [KeyboardButton("Редактировать меню")],
        [KeyboardButton("Назад")]
    ]
)

menu_admin_edit2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Добавить")],
        [KeyboardButton("Назад")]
    ]
)