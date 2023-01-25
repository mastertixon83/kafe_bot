from datetime import datetime, timezone

from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from keyboards.inline.inline_buttons import admin_inline_staff, admin_inline_send_ls, \
    user_inline_approve
from keyboards.default.menu import menuUser, menuAdmin, \
    send_phone_cancel, cancel_btn
from states.restoran import TableReservation
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from data.config import admins
import logging

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

MONTHS = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
]


### Бронирование столика
### Резервирование столика обработка данных
async def table_reservation_admin_butons(call, call_data, adminUsername, admin_id):
    # Выбрать из БД заявку
    result = await db.get_order_hall_data(id=int(call_data[2]))

    res = datetime.now(timezone.utc) - result[0]['updated_at']
    user_wait = "Гость ждал: "

    if res.days == 0:
        user_wait += f"{res.seconds // 60} минут"
    else:
        user_wait += f"{res.days} дней {res.seconds // 60} минут"

    text = ''

    if call_data[1] == 'foolrest':
        text = f"<b>Бронь пользователя</b> @{result[0]['username']} <b>отменена (Полный зал)</b>\n"
    elif call_data[1] == 'rejected':
        text = f"<b>Бронь пользователя</b> @{result[0]['username']} <b>отменена</b>\n"
    elif call_data[1] == 'approved':
        text = f"<b>Бронь пользователя</b> @{result[0]['username']} <b>подтверждена</b>\n"

    text += f"(Администратор: @{adminUsername})\n\n"
    text += user_wait + "\n"
    text += f"Комментарий: Дата/Время {result[0]['data_reservation'].strftime('%Y-%m-%d')} " \
            f"{result[0]['time_reservation']}\nКол-во человек {result[0]['number_person']}\n"
    text += f"<b>Телефон:</b> {result[0]['phone']}\n"
    admin_inline_send_ls.inline_keyboard[0][0]["url"] = f"https://t.me/{result[0]['username']}"
    await call.message.edit_text(text, reply_markup=admin_inline_send_ls, parse_mode=types.ParseMode.HTML)

    if call_data[1] in ['rejected', 'foolrest']:
        await bot.send_message(chat_id=call_data[0],
                               text="К сожалению, все столы забронированы.😞 Если что-то измениться, мы свяжемся с Вами позже 🤝")
    elif call_data[1] == 'approved':
        await bot.send_message(chat_id=call_data[0], text="Ваша запись подтвердждена администрацией. Ждем вас :)")

    # Обновить статус заявки в БД
    await db.update_order_hall_status(id=int(call_data[2]), order_status=True, admin_answer=call_data[1],
                                 updated_at=datetime.now(timezone.utc), admin_id=admin_id,
                                 admin_name=f'@{adminUsername}')


### Первый шаг
@dp.message_handler(Text("Забронировать стол"), state=None)
async def table_reservation(message: types.Message, state: FSMContext):
    await TableReservation.data.set()

    date = datetime.now().strftime('%d.%m.%Y').split('.')
    text = f"<b>Шаг [1/4]</b>\n\n Введите дату в формате ДД.ММ.ГГГГ (07.10.1985) Сегодня {date[0]} {MONTHS[int(date[1]) - 1]} {date[2]} года"
    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

    async with state.proxy() as data:
        data["chat_id"] = message.chat.id
        data["user_name"] = message.from_user.username
        data["user_id"] = message.from_user.id
        data['full_name'] = message.from_user.full_name


# Ловим ответ от пользователя дата
@dp.message_handler(content_types=["text"], state=TableReservation.data)
async def table_reservation_time(message: types.Message, state: FSMContext):
    try:
        date = message.text
        if len(date.split('.')) == 3:
            if (len(date.split('.')[0]) == 2) and (len(date.split('.')[1]) == 2) and (len(date.split('.')[2]) == 4):
                if datetime.strptime(date, "%d.%m.%Y") < datetime.now():
                    raise Exception('data error')
                else:
                    async with state.proxy() as data:
                        data["data"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()
                    await TableReservation.next()

                    text = "<b>Шаг [2/4]</b>\n\n Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
                    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)
        else:
            raise Exception("input error")
    except Exception as _ex:
        if str(_ex) == 'input error':
            text = "Я Вас не понимаю! Введите дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"

        elif str(_ex) == 'data error':
            text = "Вы путешественник во времени? Нельзя забронировать столик на прошлое.\n" \
                   "Введите правильную дату в формате ДД.ММ.ГГГГ (07.10.1985)"

        await message.answer(text=text)
        return


# Ловим ответ от пользователя время
@dp.message_handler(content_types=["text"], state=TableReservation.time)
async def table_reservation_time(message: types.Message, state: FSMContext):
    msg = message.text
    text = ''
    data = await state.get_data()
    try:
        if len(msg) == 5:
            if " " in msg:
                msg = msg.replace(" ", ":")
            elif "." in msg:
                msg = msg.replace(".", ":")
            elif "-" in msg:
                msg = msg.replace("-", ":")

            msg = msg + ":00"

            time = datetime.strptime(msg, '%H:%M:%S').time()
            if data['data'] == datetime.now() and time < datetime.now().time():
                raise Exception('time error')
            else:
                await TableReservation.next()

                async with state.proxy() as data:
                    data["time"] = time.strftime("%H:%M:%S")

                await message.answer("<b>ШАГ [3/4]</b> Введите количество человек", reply_markup=cancel_btn,
                                     parse_mode=types.ParseMode.HTML)
    except Exception as _ex:
        if str(_ex) == 'time error':
            text = "Вы путешественник во времени? Невозможно записаться на время указанное вами. Введите время заново в " \
                   "формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
        else:
            text = "Я вас, к сожалению, не понимаю. Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"

        await message.answer(text=text)
        return


# Количество человек
@dp.message_handler(content_types=["text"], state=TableReservation.count_men)
async def table_reservation_time(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await TableReservation.next()

        async with state.proxy() as data:
            data["count_mans"] = int(message.text)

        await message.answer("<b>ШАГ [4/4]</b> ⬇️ Отправьте номер телефона", reply_markup=send_phone_cancel,
                             parse_mode=types.ParseMode.HTML)

    else:
        text = "Я вас, к сожалению, не понимаю. Введите количество приглашенных человек"
        await message.answer(text=text)
        return


# Отправка контакта
@dp.message_handler(content_types=["contact", "text"], state=TableReservation.phone)
async def table_reservation_user_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await TableReservation.next()
    async with state.proxy() as data:
        if message.content_type == 'contact':
            if message.contact.phone_number[0] != "+":
                data["phone_number"] = "+" + message.contact.phone_number
            else:
                data["phone_number"] = message.contact.phone_number
            data["name"] = message.contact.last_name
        else:
            data["phone_number"] = message.text
            data["name"] = message.from_user.username

    text = "Проверьте введенные данные:\n\n"
    # d = data["date"][:-3]
    date = data['data'].strftime('%d.%m.%Y').split('.')
    text += f"Дата и время: {date[0]} {MONTHS[int(date[1]) - 1]} {date[2]} года в  {data['time'][:-3]}\n"
    text += f"Количество человек: {data['count_mans']}\n"
    text += f"Номер телефона: {data['phone_number']}"

    await message.answer(text, reply_markup=ReplyKeyboardRemove())

    await message.answer("Если всё правильно, подтвердите", reply_markup=user_inline_approve)


# Подтверждение,изменение заявки пользователем
@dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"],
                           state=TableReservation.check)
async def table_reservation_check_data(call, state: FSMContext):
    await call.answer(cache_time=60)
    if call.data == "approve_order_user":
        data = await state.get_data()

        await call.message.edit_text("Если всё правильно, подтвердите", reply_markup="")

        if call.message.from_user.id == admins[0]:
            ##TODO: Изменить меню
            await call.message.answer("⏳Один момент сейчас с Вами свяжется наш сотрудник",
                                      reply_markup=menuUser)
        else:
            await call.message.answer("⏳Один момент сейчас с Вами свяжется наш сотрудник",
                                      reply_markup=menuUser)

        text = f"Пользователь @{data['user_name']} забронировал столик\n\n"
        date = data['data'].strftime('%d.%m.%Y').split('.')
        text += f"Дата и время: {date[0]} {MONTHS[int(date[1]) - 1]} {date[2]} года на {data['time'][:-3]}\n"
        text += f"Количество человек: {data['count_mans']}\n\n"
        text += f"Имя: {data['name']}\n"
        text += f"Телефон: {data['phone_number']}"

        # Сохранить заявку в БД
        order_id = await db.add_new_order_hall(admin_id=None, order_status=False, chat_id=data['chat_id'],
                                          user_id=data['user_id'],
                                          username=data['user_name'], full_name=data['full_name'],
                                          data_reservation=data['data'], time_reservation=data['time'][:-3],
                                          number_person=data['count_mans'], phone=data['phone_number'])

        admin_inline_staff.inline_keyboard[2][0]["url"] = f"https://t.me/{data['user_name']}"
        admin_inline_staff.inline_keyboard[0][0]["callback_data"] = f"{data['chat_id']}-rejected-{order_id}"
        admin_inline_staff.inline_keyboard[0][1]["callback_data"] = f"{data['chat_id']}-approved-{order_id}"
        admin_inline_staff.inline_keyboard[1][0]["callback_data"] = f"{data['chat_id']}-foolrest-{order_id}"

        await bot.send_message(chat_id=admins[0], text=text, reply_markup=admin_inline_staff)
        await state.finish()

    elif call.data == "cancel_order_user":
        await call.message.edit_text("Если всё правильно, подтвердите", reply_markup="")

        text = f"<b>ШАГ [1/4]</b>\n Выберите дату\n\nСегодня {datetime.now().strftime('%d.%m.%Y')}"
        await call.message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

        await TableReservation.data.set()


# Подтверждение заявки админом
@dp.callback_query_handler(text_contains="approved")
async def table_reservation_admin(call):
    await call.answer(cache_time=60)

    call_data = call.data.split("-")
    adminUsername = call.from_user.username
    admin_id = call.from_user.id
    await table_reservation_admin_butons(call=call, call_data=call_data, adminUsername=adminUsername, admin_id=admin_id)


# Полная посадка Адмни
@dp.callback_query_handler(text_contains="foolrest")
async def table_reservation_admin_fool_rest(call):
    await call.answer(cache_time=60)

    call_data = call.data.split("-")
    adminUsername = call.from_user.username
    admin_id = call.from_user.id
    await table_reservation_admin_butons(call=call, call_data=call_data, adminUsername=adminUsername, admin_id=admin_id)


# Отклонение заявки админом
@dp.callback_query_handler(text_contains="rejected")
async def table_reservation_admin_reject(call):
    await call.answer(cache_time=60)

    call_data = call.data.split("-")
    adminUsername = call.from_user.username
    admin_id = call.from_user.id
    await table_reservation_admin_butons(call=call, call_data=call_data, adminUsername=adminUsername, admin_id=admin_id)
