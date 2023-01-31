from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menuUser = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Вызов персонала")
        ],
        [
            KeyboardButton(text="Забронировать стол")
        ],
        [
            KeyboardButton(text="Программа лояльности")
        ],
        [
            KeyboardButton(text="Меню"),
            KeyboardButton(text="Акции")
        ],
        [
            KeyboardButton(text="Доставка")
        ],
        [
            KeyboardButton(text="Написать владельцу")
        ],
        [
            KeyboardButton(text="Помощь")
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
            KeyboardButton(text="Бронь столиков")
        ],
        [
            KeyboardButton(text="Программа лояльности")
        ],
        [
            KeyboardButton(text="Меню"),
            KeyboardButton(text="Акции")
        ],
        [
            KeyboardButton(text="Доставка")
        ],
        [
            KeyboardButton(text="Написать владельцу")
        ],
        [
            KeyboardButton(text="Сделпть рассылку подписчикам")
        ],
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Аналитика")
        ],
        [
            KeyboardButton(text="Помощь")
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
        [KeyboardButton("Пригласить друга")],
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