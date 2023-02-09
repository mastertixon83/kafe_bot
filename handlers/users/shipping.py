from datetime import datetime, timezone

from aiogram.dispatcher import FSMContext

from handlers.users.hall_reservation import MONTHS
from loader import dp, bot, db
from aiogram import types

from keyboards.inline.inline_buttons import admin_inline_staff, admin_inline_send_ls, \
    user_inline_approve

from keyboards.default.menu import menuUser, menuAdmin, \
    send_phone_cancel, cancel_btn

from states.shipping import Shipping
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from data.config import admins

db = DBCommands()


### Ловлю от пользователя название блюда
@dp.message_handler(content_types=["text"], state=Shipping.title_item)
async def shipping_title(message: types.Message, state: FSMContext):
    await Shipping.portion_quantity.set()

    async with state.proxy() as data:
        data['title'] = message.text

    text = "<b>Шаг [2/7]</b> Введите количество порций"
    await message.answer(text=text, reply_markup=cancel_btn)


### Ловлю от пользователя количество порций
@dp.message_handler(content_types=["text"], state=Shipping.portion_quantity)
async def shipping_portion_quantity(message: types.Message, state: FSMContext):
    await Shipping.number_of_devices.set()

    async with state.proxy() as data:
        data['portion_quantity'] = message.text

    text = "<b>Шаг [3/7]</b> На какое количество человек положить приборов?"
    await message.answer(text=text, reply_markup=cancel_btn)


### Ловлю от пользователя количество приборов
@dp.message_handler(content_types=["text"], state=Shipping.number_of_devices)
async def shipping_number_of_devices(message: types.Message, state: FSMContext):
    await Shipping.data.set()

    async with state.proxy() as data:
        data['number_of_devices'] = message.text

    date = datetime.now().strftime('%d.%m.%Y').split('.')
    text = "<b>Шаг [4/7]</b> На какую дату вы хотите заказать доставку?\n"
    text += f"Введите дату в формате ДД.ММ.ГГГГ (07.10.1985) Сегодня {date[0]} {MONTHS[int(date[1]) - 1]} {date[2]} года"
    await message.answer(text=text, reply_markup=cancel_btn)


### Ловлю от пользователя дату доставки
@dp.message_handler(content_types=["text"], state=Shipping.data)
async def shipping_number_of_devices(message: types.Message, state: FSMContext):
    # await Shipping.time.set()
    #
    # async with state.proxy() as data:
    #     data['data'] = message.text
    #
    # text = "<b>Шаг [5/7]</b> К какому времени доставить?"
    # await message.answer(text=text, reply_markup=cancel_btn)
    try:
        date = message.text
        if len(date.split('.')) == 3:
            if (len(date.split('.')[0]) == 2) and (len(date.split('.')[1]) == 2) and (len(date.split('.')[2]) == 4):
                if datetime.strptime(date, "%d.%m.%Y") < datetime.now():
                    raise Exception('data error')
                else:
                    async with state.proxy() as data:
                        data["data"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()

                    await Shipping.time.set()

                    text = "<b>Шаг [5/7]</b>\n\n Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
                    await message.answer(text, parse_mode=types.ParseMode.HTML)
        else:
            raise Exception("input error")
    except Exception as _ex:
        if str(_ex) == 'input error':
            text = f"Я Вас не понимаю! Введите дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"

        elif str(_ex) == 'data error':
            text = f"Вы путешественник во времени? Нельзя заказать доставку в прошлое.\n" \
                   f"Введите правильную дату в формате ДД.ММ.ГГГГ (07.10.1985)"

        await message.answer(text=text)
        return



### Ловлю от пользователя время доставки
@dp.message_handler(content_types=["text"], state=Shipping.time)
async def shipping_time(message: types.Message, state: FSMContext):
    # async with state.proxy() as data:
    #     data['time'] = message.text
    #
    # text = "<b>Шаг [6/7]</b> Введите адрес доставки"
    # await message.answer(text=text, reply_markup=cancel_btn)
    msg = message.text
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
                await Shipping.address.set()

                async with state.proxy() as data:
                    data["time"] = time.strftime("%H:%M:%S")

                await message.answer("<b>Шаг [6/7]</b> Введите адрес доставки",
                                     parse_mode=types.ParseMode.HTML)
    except Exception as _ex:
        if str(_ex) == 'time error':
            text = "Вы путешественник во времени? Невозможно заказать доставку на время указанное вами. Введите время заново в " \
                   "формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
        else:
            text = "Я Вас, к сожалению, не понимаю. Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"

        await message.answer(text=text)
        return


### Ловлю от пользователя адресс доставки
@dp.message_handler(content_types=["text"], state=Shipping.address)
async def shipping_time(message: types.Message, state: FSMContext):
    await Shipping.phone.set()

    async with state.proxy() as data:
        data['address'] = message.text

    text = "<b>Шаг [7/7]</b> Введите Ваш контактный номер телефона "
    await message.answer(text=text, reply_markup=send_phone_cancel)


### Ловлю от пользователя номер телефона
@dp.message_handler(content_types=["contact", "text"], state=Shipping.phone)
async def shipping_time(message: types.Message, state: FSMContext):
    await Shipping.check.set()

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

    data = await state.get_data()

    text = f"""{data['name']}, Ваш заказ\n
    1️⃣ {data['title']}\n
    2️⃣ {data['portion_quantity']}\n
    3️⃣ {data['number_of_devices']}\n
    4️⃣ {data['data']}\n
    5️⃣ {data['time']}\n
    6️⃣ {data['address']}\n
    7️⃣ {data['phone_number']}\n\n
"""
    await message.answer(text=text, reply_markup="")
    await message.answer("Если всё правильно, подтвердите", reply_markup=user_inline_approve)


### Ловлю ответ от пользователя о проверке данных
@dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"], state=Shipping.check)
async def shipping_user_check_data(call, state: FSMContext):
    await call.answer(cache_time=60)

    if call.data == "approve_order_user":
        print("approved")
    elif call.data == "cancel_order_user":
        print("canceled")
    await state.finish()