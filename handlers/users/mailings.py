import os
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data import config
from handlers.users import apsched

from loader import dp, bot, db, scheduler, logger
from aiogram import types

from keyboards.default.menu import cancel_btn, newsletter_kbd
from aiogram.dispatcher import FSMContext
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text

from states.mailings import Mailings

db = DBCommands()


@dp.message_handler(
    Text(contains="Обычная рассылка") | Text(contains="Предложение для именинников") |
    Text(contains="Призыв к бронированию") | Text(contains="Закажите доставку") |
    Text(contains="Владельцам карт лояльности") | Text(contains="Конкретным пользователям"),
    state=Mailings.main
)
async def taking_type_mailing(message: types.Message, state: FSMContext):
    """Ловлю выбор рассылки"""

    if "Обычная рассылка" in message.text.strip():
        type_mailing = "standard"
        users = await db.get_all_nb_users()

    elif "Предложение для именинников" in message.text.strip():
        type_mailing = "birthday"
        before_birthday_days = config.BEFORE_BIRTHDAY_DAYS
        delta = timedelta(days=int(before_birthday_days))
        current_data = datetime.now().date()
        target_data = current_data + delta
        users = await db.get_birthday_users(target_data=target_data)

    elif "Призыв к бронированию" in message.text.strip():
        type_mailing = "hall_reservation"
        users = await db.get_all_nb_users()

    elif "Закажите доставку" in message.text.strip():
        type_mailing = "shipping"
        users = await db.get_all_nb_users()

    elif "Владельцам карт лояльности" in message.text.strip():
        type_mailing = "loyal_card"
        users = await db.get_loyal_program_participants()

    # elif "Конкретным пользователям" in message.text.strip():
    #     type_mailing = "users"
    #     users = db.get_all_users()

    else:
        type_mailing = "None"
        users = []

    await Mailings.mailing_picture.set()

    data = await state.get_data()

    text = "Загрузите изображение для рассылки"
    msg = await message.answer(text=text, reply_markup=cancel_btn)

    id_msg_list = []
    try:
        id_msg_list = data['id_msg_list']
    except Exception as _ex:
        pass

    id_msg_list.append(msg.message_id)
    id_user_list = [{'user_id': user['user_id'].strip(), 'administrator': user['administrator']} for user in users]

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['admin_name'] = message.from_user.username
        data['type_mailing'] = type_mailing
        data['users'] = id_user_list

    await message.delete()


@dp.message_handler(lambda message: not message.photo, state=Mailings.mailing_picture)
async def check_standard_mailing_photo(message: types.Message, state: FSMContext):
    """Проверка на тип сообщения, картинка или нет"""
    await message.delete()

    data = await state.get_data()

    text = "Это не изображение!\n\n"
    text += "Загрузите изображение для рассылки"

    return await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Mailings.mailing_picture)
async def mailing_picture(message: types.Message, state: FSMContext):
    """Ловлю изображение для рассылки"""
    await Mailings.mailing_text.set()
    data = await state.get_data()
    try:
        await message.photo[-1].download(f"media/mailings/{data['type_mailing']}_{message.photo[-1].file_id}.jpg")
    except Exception as _ex:
        os.mkdir("media/mailings")
        await message.photo[-1].download(f'media/mailings/standard_{message.photo[-1].file_id}.jpg')

    data = await state.get_data()

    text = "Введите сообщение рассылки"
    msg = await message.answer(text=text, reply_markup=cancel_btn)

    id_msg_list = []
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['mailing_picture'] = message.photo[-1].file_id


@dp.message_handler(content_types=["text"], state=Mailings.mailing_text)
async def mailing_text(message: types.Message, state: FSMContext):
    """Ловлю текст рассылки"""

    data = await state.get_data()
    id_msg_list = []
    keyboard = ""
    id_msg_list = data['id_msg_list']

    message_text = message.text.strip()

    if data["type_mailing"] not in ["hall_reservation", "shipping"]:
        await Mailings.sending_button.set()
        text = "Выберите какую кнопку прикрепить к сообщению"
        msg = await message.answer(text=text)
        id_msg_list.append(msg.message_id)

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🍽 Забронировать стол", callback_data="hall_reservation")],
                [InlineKeyboardButton(text="🚚 Заказать доставку", callback_data="shipping")],
                [InlineKeyboardButton(text="Никакую", callback_data="None")],
            ]
        )

        msg = await message.answer(text="Выберите кнопку", reply_markup=markup)
        id_msg_list.append(msg.message_id)
    else:
        await Mailings.sending_method.set()

        data = await state.get_data()

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Указать дату", callback_data="delayed_mailing")],
            [InlineKeyboardButton(text="📤 Отправить немедленно", callback_data="send_immediately")]
        ])

        msg = await message.answer(text="Выберите действие", reply_markup=markup)

        id_msg_list.append(msg.message_id)
        keyboard = data["type_mailing"]

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['message_text'] = message_text
        data['keyboard'] = keyboard


@dp.callback_query_handler(text=["hall_reservation", "shipping", "None"], state=Mailings.sending_button)
async def mailing_buttons(call: types.CallbackQuery, state: FSMContext):
    """Ловлю выбор какую кнопку прикрепить"""
    await Mailings.sending_method.set()

    data = await state.get_data()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Указать дату", callback_data="delayed_mailing")],
        [InlineKeyboardButton(text="📤 Отправить немедленно", callback_data="send_immediately")]
    ])
    if data["type_mailing"] == "birthday":
        markup.row(InlineKeyboardButton(text="💾 Сохранить", callback_data="save_task"))

    await call.message.edit_text(text="Выберите действие")
    await call.message.edit_reply_markup(reply_markup=markup)
    keyboard = call.data
    async with state.proxy() as data:
        data['keyboard'] = keyboard


@dp.callback_query_handler(text=["delayed_mailing", "send_immediately", "save_task"],
                           state=Mailings.sending_method)
async def mailing_sending_method(call: types.CallbackQuery, state: FSMContext):
    """Ловлю от пользователя способ отправки"""
    await call.answer()

    data = await state.get_data()
    admin_name = data["admin_name"]
    type_mailing = data["type_mailing"]
    picture = data["mailing_picture"]
    message_text = data["message_text"]
    id_msg_list = data["id_msg_list"]
    users = data['users']
    keyboard = data['keyboard']

    if (call.data == "send_immediately") or (call.data == "save_task"):
        # Отпраивть немедленно
        date = datetime.now()
        minute_later = date + timedelta(seconds=5)

        await db.update_before_adding(type_mailing=type_mailing)

        task_id = await db.add_new_task(admin_name=admin_name, type_mailing=type_mailing, picture=picture,
                                        message=message_text, status="waiting",
                                        execution_date=datetime(minute_later.year, minute_later.month, minute_later.day,
                                                                minute_later.hour, minute_later.minute),
                                        error="No errors", keyboard=keyboard)
        if call.data != "save_task":
            try:
                if users:
                    scheduler.add_job(
                        apsched.send_message_date, 'date', run_date=minute_later, id=type_mailing,
                        kwargs={'bot': bot, 'task_id': task_id, 'users': users, 'type_mailing': type_mailing,
                                'keyboard': keyboard}
                    )
                    text = f"Рассылка запланирована на {minute_later.strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    text = "Нет пользователей для рассылки"
            except Exception as _ex:
                text = f"Рассылка не запланирована - Ошибка: {_ex}"
                await db.update_task(task_id=int(task_id), status="error", error=_ex)
        else:
            text = "Рассылка сохранена"

        await call.message.delete()
        msg = await call.message.answer(text=text, reply_markup=newsletter_kbd)
        id_msg_list.append(msg.message_id)

        await state.finish()
        await Mailings.main.set()

        async with state.proxy() as data:
            data["id_msg_list"] = id_msg_list

    elif call.data == "delayed_mailing":
        # Отпраивть в указанную дату
        await Mailings.sending_data.set()
        await call.message.delete()
        text = f"Укажите время и дату рассылки в формате ГГГГ-ММ-ДД ЧЧ:ММ \n\nСегодня {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        await call.message.answer(text=text)


@dp.message_handler(content_types=["text"], state=Mailings.sending_data)
async def standard_mailing_date_time(message: types.Message, state: FSMContext):
    """Ловлю дату и время рассылки"""
    date = message.text.strip() + ":00"

    data = await state.get_data()

    admin_name = data["admin_name"]
    type_mailing = data["type_mailing"]
    picture = data["mailing_picture"]
    message_text = data["message_text"]
    id_msg_list = data["id_msg_list"]
    users = data["users"]
    keyboard = data["keyboard"]

    try:
        # Отключение всех рассылок данного типа, чтобы не размножались
        await db.update_before_adding(type_mailing=type_mailing)

        task_id = await db.add_new_task(admin_name=admin_name, type_mailing=type_mailing, picture=picture,
                                        message=message_text, status="waiting",
                                        execution_date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
                                        error="No error", keyboard=keyboard)
        try:
            if users:
                scheduler.add_job(
                    apsched.send_message_date, 'date', run_date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
                    id=type_mailing,
                    kwargs={'bot': bot, 'task_id': task_id, 'users': users, 'type_mailing': type_mailing,
                            'keyboard': keyboard}
                )
                text = f"Рассылка запланирована на {datetime.strptime(date, '%Y-%m-%d %H:%M:%S')}"
            else:
                text = "Нет пользователей для рассылки"
        except Exception as _ex:
            logger.error(f"Рассылка не запланирована - Ошибка: {_ex}")
            text = f"Рассылка не запланирована - Ошибка: {_ex}"
            await db.update_task(task_id=int(task_id), status="error", error=_ex)

        msg = await message.answer(text=text, reply_markup=newsletter_kbd)

        id_msg_list.append(msg.message_id)

        await state.finish()
        await Mailings.main.set()

        async with state.proxy() as data:
            data["id_msg_list"] = id_msg_list

    except Exception as _ex:
        logger.error(f"{_ex}")
        await message.answer(text="Я Вас не понимаю. Введите корректные данные в формате ГГГГ-ММ-ДД ЧЧ:ММ")
