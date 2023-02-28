import re
from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import datetime, timezone

from data.config import admins
from keyboards.inline import user_inline_approve
from states.shipping import Shipping

from keyboards.default import cancel_btn, menuAdmin, send_phone_cancel, menuUser
from keyboards.inline.inline_user_order_shipping import categories_keyboard, menu_cd, \
    items_in_category_keyboard, make_callback_data

from loader import dp, bot
from states.config import MainMenu
from utils.db_api.db_commands import DBCommands

db = DBCommands()


@dp.message_handler(Text(contains="Оформить заказ на доставку"), state=None)
async def show_menu_order_shipping(message: types.Message, state: FSMContext):
    await message.delete()
    await db.delete_cart(str(message.chat.id))
    await message.answer('Оформление заказа на доставку', reply_markup=ReplyKeyboardRemove())
    await build_category_keyboard(message)

    async with state.proxy() as data:
        data["message_id"] = message.message_id + 2
        data["chat_id"] = message.from_user.id


###Ловлю нажатие любой инлайн кнопки
@dp.callback_query_handler(menu_cd.filter(), state="*")
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get('level')
    category_id = callback_data.get('category_id')
    item_id = callback_data.get('item_id')
    action = callback_data.get('action')
    what = callback_data.get('what'),
    minus = callback_data.get('minus'),
    count = callback_data.get('count'),
    plus = callback_data.get('plus'),
    st = state

    levels = {
        "-1": main_menu,
        # "0": what_to_edit,
        "1": build_category_keyboard,
        "2": build_item_cards,
        "3": delivery_registration,
        # "12": new_category,
        # "13": delete_category,
        # "14": edit_position_category,
        # "22": new_item,
        # "23": delete_item,
        "221": add_order_item,
        "222": del_order_item
    }

    current_level_functions = levels[current_level]
    await current_level_functions(
        call,
        category_id=category_id,
        item_id=item_id,
        action=action,
        what=what,
        minus=minus,
        count=count,
        plus=plus,
        state=st
    )


### Ловлю нажатие кнопки выход
async def main_menu(callback: types.CallbackQuery, what, state, **kwargs):
    await callback.message.delete()
    await callback.message.answer(text="Главное меню", reply_markup=menuAdmin)
    user_id = callback.message.chat.id
    await db.delete_cart(user_id=str(user_id))
    await state.finish()


### Построение клавиатуры категорий, после нажатия на кнопку Оформить заказ на доставку
async def build_category_keyboard(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard()
    if kwargs:
        data = await kwargs['state'].get_data()
        for msg_id in data['message_id_list']:
            await bot.delete_message(chat_id=message.from_user.id, message_id=msg_id)

    if isinstance(message, types.Message):
        await message.answer("Что будешь заказывать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будешь заказывать?", reply_markup=markup)


### Построение карточек блюд, после выбора категории
async def build_item_cards(callback: types.CallbackQuery, category_id, state, **kwargs):
    category_info = await db.get_category_info(id=int(category_id))

    msg = await callback.message.edit_text(f"Блюда категории {category_info[0]['title']}")

    items = await db.get_all_items_in_category(category_id=int(category_id))
    message_id_list = [msg.message_id]
    data = await state.get_data()

    for item in items:
        item_id = item['id']
        info = await db.get_item_info(id=int(item_id))

        markup = await items_in_category_keyboard(item_id=int(item['id']), count=0, user_id=data['chat_id'])

        msg = await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=info[0]['photo'],
            caption=f"{info[0]['description']}\n Цена: {str(item['price'])[:-3]} тенге.",
            parse_mode="HTML",
            reply_markup=markup
        )

        message_id_list.append(msg.message_id)

    async with state.proxy() as data:
        data['message_id_list'] = message_id_list

    markup2 = InlineKeyboardMarkup()
    markup2.add(
        InlineKeyboardButton(text="Назад",
                             callback_data=make_callback_data(level=1,
                                                              what='back_order_shipping'))
    )
    await callback.message.answer(text="Добавить другие блюда", reply_markup=markup2)


### Добавление блюда в корзину
async def add_order_item(callback: types.CallbackQuery, **kwargs):
    count = int(kwargs['count'][0])
    item_id = kwargs['item_id']

    user_id = callback.message.chat.id
    markup = await items_in_category_keyboard(item_id=kwargs['item_id'], count=count + 1)
    info = await db.get_item_info(id=int(kwargs['item_id']))
    try:
        cart_id = await db.update_cart(item_id=int(item_id),
                                       item_count=count + 1,
                                       user_id=str(user_id),
                                       title=info[0]['title'],
                                       price=info[0]['price'])
        if cart_id == []:
            raise Exception("Record not found")
    except Exception as _ex:
        cart_id = await db.add_new_cart(item_id=int(item_id),
                                        item_count=count + 1,
                                        user_id=str(user_id),
                                        title=info[0]['title'],
                                        price=info[0]['price']
                                        )

    await callback.message.edit_reply_markup(markup)


### Отнимание блюда из корзины
async def del_order_item(callback: types.CallbackQuery, **kwargs):
    count = int(kwargs['count'][0])

    if count > 0:
        item_id = kwargs['item_id']
        user_id = callback.message.chat.id
        markup = await items_in_category_keyboard(item_id, count=count - 1)
        try:
            cart_id = await db.update_cart(item_id=int(item_id), item_count=count - 1, user_id=str(user_id))
            if cart_id == []:
                raise Exception("Record not found")
        except Exception as _ex:
            cart_id = await db.add_new_cart(item_id=int(item_id), item_count=count - 1, user_id=str(user_id))
        await callback.message.edit_reply_markup(markup)


### Ловлю нажатие на кнопку Оформить доставку
async def delivery_registration(callback: types.CallbackQuery, **kwargs):
    await callback.message.delete()
    await Shipping.data.set()

    date = datetime.now().strftime('%d.%m.%Y').split('.')
    text = "На какую дату оформить доставку?\n"
    text += f"Введи дату в формате ДД.ММ.ГГГГ \n Сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

    await callback.message.answer(text=text, reply_markup=cancel_btn)


### Ловлю от пользователя дату доставки
@dp.message_handler(content_types=["text"], state=Shipping.data)
async def shipping_data(message: types.Message, state: FSMContext):
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

                    text = "К какому времени доствить? Введи время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
                    await message.answer(text, parse_mode=types.ParseMode.HTML)
        else:
            raise Exception("input error")
    except Exception as _ex:
        if (str(_ex) == 'input error') or (str(_ex) == 'day is out of range for month'):
            text = f"К сожалению я Тебя не понимаю, введит корректную дату в правильном формате ДД.ММ.ГГГГ, сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

        elif str(_ex) == 'data error':
            #К сожалению время не вернуть назад, укажите корректную дату, сегодня 24.02.2023
            text = f"К сожалению время не вернуть назад 😢 Введи корректную дату в формате ДД.ММ.ГГГГ, сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

        text = ""
        await message.answer(text=text)
        return


### Ловлю от пользователя время доставки
@dp.message_handler(content_types=["text"], state=Shipping.time)
async def shipping_time(message: types.Message, state: FSMContext):
    await Shipping.number_of_devices.set()
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

                await message.answer("Сколько приборов потребуется?",
                                     parse_mode=types.ParseMode.HTML)
    except Exception as _ex:
        if str(_ex) == 'time error':
            text = "К сожалению время не вернуть назад 😢 Введи корректное время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
        else:
            text = "Я Тебя, к сожалению, не понимаю. Введи время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"

        await message.answer(text=text)
        return


### Ловлю от пользователя кол-во приборов
@dp.message_handler(content_types=["text"], state=Shipping.number_of_devices)
async def shipping_number_of_devices(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await Shipping.address.set()
        async with state.proxy() as data:
            data['number_of_devices'] = message.text

        date = datetime.now().strftime('%d.%m.%Y').split('.')
        text = "Введи адрес доставки\n"
        await message.answer(text=text, reply_markup=cancel_btn)
    else:
        text = "К сожалению я Тебя не понимаю, введи корректные данные!!! \nСколько приборов потребуется?"
        await message.answer(text=text, reply_markup=cancel_btn)


### Ловлю от пользователя адрес доставки
@dp.message_handler(content_types=["text"], state=Shipping.address)
async def shipping_address(message: types.Message, state: FSMContext):
    await Shipping.phone.set()

    text = "Введи или отправь Свой контактный номер телефона "
    msg = await message.answer(text=text, reply_markup=send_phone_cancel)

    async with state.proxy() as data:
        data['address'] = message.text
        data['message_id'] = msg.message_id


### Ловлю от пользователя контактный номер телефона
@dp.message_handler(content_types=["contact", "text"], state=Shipping.phone)
async def shipping_address(message: types.Message, state: FSMContext):
    await Shipping.pay_method.set()

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

    text = "💳 vs 💵"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="💳 Карта", callback_data="pay_method_card"),
        InlineKeyboardButton(text="💵 Наличка", callback_data="pay_method_money"),
    )
    await message.answer(text="Выбери способ оплаты", reply_markup=markup)


### Ловлю от пользователя способ оплаты
@dp.callback_query_handler(text=["pay_method_card", "pay_method_money"], state=Shipping.pay_method)
async def shipping_pay_method(call: types.CallbackQuery, state: FSMContext):
    await Shipping.check.set()
    await call.message.edit_reply_markup(reply_markup="")

    cart_info = await db.cart_info(user_id=str(call.message.chat.id))
    async with state.proxy() as data:
        data['pay_method'] = call.data

    text = "Ваш заказ\n"
    summa = 0
    for item in cart_info:
        text += f"{item['title']}\nКол-во порций: {item['item_count']}\nЦена: {item['price']}\n\n"
        summa += item['item_count'] * item['price']

    text += f"Общая сумма заказа: {summa}"
    await call.message.answer(text=text, reply_markup=cancel_btn)

    await call.message.answer(text=text, reply_markup=user_inline_approve)


### Ловлю от пользователя проверка
@dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"], state=Shipping.check)
async def shipping_user_check_data(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup="")
    await call.message.delete()

    await call.answer(cache_time=60)

    if call.data == "approve_order_user":
        data = await state.get_data()

        order_id = await db.add_new_shipping_order(
            title=data['title'],
            number_of_devices=int(data['number_of_devices']),
            address=data['address'], phone=data['phone_number'], data_reservation=data['data'],
            time_reservation=data['time'][:-3], pay_method=data['pay_method'], user_id=str(data['user_id']),
            user_name=data['user_name']
        )
        text = f"{data['user_name']} Твоя заявка отправлена нашему сотруднику. Ожидай. Он с Тобой скоро свяжется"
        await call.message.answer(text=text, reply_markup=menuUser)
        text = "Поступила заявка на доставку\n"
        text += f"Пользователь @{data['user_name']} заказал:\n"

        text += f"Количество приборов: {data['number_of_devices']}\n"
        text += f"Дата доставки: {data['data']}\n"
        text += f"Время доставки: {data['time']}\n"
        text += f"Адрес доставки: {data['address']}\n"
        if data['pay_method'] == "pay_method_card":
            text += "Способ оплаты: Карта\n"
        elif data['pay_method'] == "pay_method_money":
            text += "Способ оплаты: Наличные\n"
        text += f"Контактный номер телефона: {data['phone_number']}\n"

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(text="Взять в работу", callback_data=f"admin_approve_shipping-{order_id}"),
            InlineKeyboardButton(text="Отмена", callback_data=f"admin_cancel_shipping-{order_id}")
        )
        markup.row(
            InlineKeyboardButton("Написать гостю в ЛС", callback_data=f"shipping_write_to_pm-{order_id}",
                                 url=f"https://t.me/{data['user_name']}")
        )

        await bot.send_message(chat_id=admins[0], text=text, reply_markup=markup)
        await state.finish()

    elif call.data == "cancel_order_user":
        await Shipping.data.set()
        text = "Главное меню"
        await call.message.answer(text=text, reply_markup=menuUser)