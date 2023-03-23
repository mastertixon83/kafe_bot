import json
import re
import time
from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from datetime import datetime, timezone

from data.config import admins
from keyboards.inline import user_inline_approve
from states.shipping import Shipping

from keyboards.default import cancel_btn, menuAdmin, send_phone_cancel, menuUser, send_phone
from keyboards.inline.inline_user_order_shipping import categories_keyboard, menu_cd, \
    items_in_category_keyboard, make_callback_data

from loader import dp, bot
from states.config import MainMenu
from utils.db_api.db_commands import DBCommands

db = DBCommands()


###Ловлю нажатие любой инлайн кнопки
@dp.callback_query_handler(menu_cd.filter(), state="*")
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Главный обработчик нажатий на кнопки"""
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
        "222": del_order_item,
        "999": cart
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


async def cart(callback: types.CallbackQuery, what, state, **kwargs):
    """Корзина пользователя"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Корзина пользователя')
    msg = await callback.message.edit_text("Корзина пользователя")
    items = await db.get_user_cart(user_id=callback.message.chat.id)
    message_id_list = [msg.message_id]
    data = await state.get_data()
    sum = 0
    for item in items:
        sum += item["item_count"] * item["price"]
        item_id = item['item_id']
        info = await db.get_item_info(id=int(item_id))

        markup = await items_in_category_keyboard(item_id=int(item_id), count=item["item_count"],
                                                  user_id=data['chat_id'])

        msg = await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=info[0]['photo'],
            caption=f"{info[0]['description']}\nЦена: {str(item['price'])[:-3]} тенге.",
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
    msg = await callback.message.answer(text=f"Сумма Вашего заказа {sum}", reply_markup=markup2)
    async with state.proxy() as data:
        data["sum_id"] = msg.message_id


async def main_menu(callback: types.CallbackQuery, what, state, **kwargs):
    """Обработчик нажатия на кнопку выход"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Доставка Главное меню')
    await callback.message.delete()
    await callback.message.answer(text="Главное меню", reply_markup=menuAdmin)
    user_id = callback.message.chat.id
    await db.delete_cart(user_id=str(user_id))
    await state.finish()


async def build_category_keyboard(message: Union[types.Message, types.CallbackQuery], **kwargs):
    """Построение клавиатуры категорий, после нажатия на кнопку Оформить заказ на доставку"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка клавиатура категорий')
    markup = await categories_keyboard(user_id=message.from_user.id)
    if kwargs:
        data = await kwargs['state'].get_data()
        for msg_id in data['message_id_list']:
            await bot.delete_message(chat_id=message.from_user.id, message_id=msg_id)

    if isinstance(message, types.Message):
        await message.answer("Что будете заказывать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будете заказывать?", reply_markup=markup)


async def build_item_cards(callback: types.CallbackQuery, category_id, state, **kwargs):
    """Построение карточек блюд, после выбора категориии"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Доставка построение карточек блюд')
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
            caption=f"{info[0]['description']}\n{'-'*50}\nЦена: {str(item['price'])[:-3]} тенге.",
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
    msg = await callback.message.answer(text="Добавить другие блюда", reply_markup=markup2)
    async with state.proxy() as data:
        data["sum_id"] = msg.message_id


async def add_order_item(callback: types.CallbackQuery, state, **kwargs):
    """Добавление блюда в корзину"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Доставка добавление блюда в корзину')
    count = int(kwargs['count'][0])
    item_id = kwargs['item_id']
    data = await state.get_data()

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

    user_cart = await db.get_user_cart(user_id=user_id)
    sum = 0
    for item in user_cart:
        sum += item["price"] * item["item_count"]
    await callback.message.edit_reply_markup(markup)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=data["sum_id"],
                                text=f"Сумма Вашего заказа {sum}")
    markup2 = InlineKeyboardMarkup()
    markup2.add(
        InlineKeyboardButton(text="Назад",
                             callback_data=make_callback_data(level=1,
                                                              what='back_order_shipping'))
    )
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=data["sum_id"],
                                        reply_markup=markup2)


async def del_order_item(callback: types.CallbackQuery, state, **kwargs):
    """Удаление блюда из корзины"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Доставка удаление блюда из корзины')
    count = int(kwargs['count'][0])
    item_id = kwargs['item_id']
    data = await state.get_data()
    if count > 0:

        user_id = callback.message.chat.id
        info = await db.get_item_info(id=item_id)

        markup = await items_in_category_keyboard(int(item_id), count=count - 1)

        try:
            cart_id = await db.update_cart(
                item_id=int(item_id),
                item_count=count - 1,
                user_id=str(user_id),
                title=info[0]['title'],
                price=info[0]['price']
            )
            if cart_id == []:
                raise Exception("Record not found")
        except Exception as _ex:
            cart_id = await db.add_new_cart(
                item_id=int(item_id),
                item_count=count - 1,
                user_id=str(user_id),
                title=info[0]['title'],
                price=info[0]['price']
            )
        user_cart = await db.get_user_cart(user_id=user_id)
        sum = 0
        for item in user_cart:
            sum += item["price"] * item["item_count"]
        await callback.message.edit_reply_markup(markup)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=data["sum_id"],
                                    text=f"Сумма Вашего заказа {sum}")
        markup2 = InlineKeyboardMarkup()
        markup2.add(
            InlineKeyboardButton(text="Назад",
                                 callback_data=make_callback_data(level=1,
                                                                  what='back_order_shipping'))
        )
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=data["sum_id"],
                                            reply_markup=markup2)
        if count - 1 == 0:
            await db.delete_item_From_cart(item_id=int(item_id))
            return


async def delivery_registration(callback: types.CallbackQuery, **kwargs):
    """Ловлю нажатие на кнопку оформить доставку"""
    await db.update_last_activity(user_id=callback.message.from_user.id, button='Доставка оформление заказа')
    await callback.message.delete()
    await Shipping.data.set()

    text = "На какую дату оформить доставку?\n"
    text += f"Введите дату в формате ДД.ММ.ГГГГ \n Сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

    await callback.message.answer(text=text)


@dp.message_handler(content_types=["text"], state=Shipping.data)
async def shipping_data(message: types.Message, state: FSMContext):
    """Ловлю от пользователя дату доставки"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка дата заказа')
    try:
        date = message.text
        curr_date = datetime.now().strftime("%d.%m.%Y")
        if len(date.split('.')) == 3:
            if (len(date.split('.')[0]) == 2) and (len(date.split('.')[1]) == 2) and (len(date.split('.')[2]) == 4):
                if datetime.strptime(date, "%d.%m.%Y") < datetime.strptime(curr_date, "%d.%m.%Y"):
                    raise Exception('data error')
                else:
                    async with state.proxy() as data:
                        data["data"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()
                        data["user_id"] = message.chat.id
                        data['user_name'] = message.from_user.username

                    await Shipping.time.set()

                    text = f"К какому времени доствить? Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ. Сейчас {datetime.now().time().strftime('%H:%M')}"
                    await message.answer(text, parse_mode=types.ParseMode.HTML)
        else:
            raise Exception("input error")
    except Exception as _ex:
        text = ""
        if (str(_ex) == 'input error') or (str(_ex) == 'day is out of range for month'):
            text = f"К сожалению я Вас не понимаю, введите корректную дату в правильном формате ДД.ММ.ГГГГ. Сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

        elif str(_ex) == 'data error':
            text = f"К сожалению время не вернуть назад 😢 Введите корректную дату в формате ДД.ММ.ГГГГ, Сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"

        await message.answer(text=text)
        return


@dp.message_handler(content_types=["text"], state=Shipping.time)
async def shipping_time(message: types.Message, state: FSMContext):
    """Ловлю от пользователя время доставки"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка время заказа')
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
            curr_time = datetime.now().time()
            curr_date = datetime.now().date()
            if data['data'] == curr_date and time < curr_time:
                raise Exception('time error')
            else:
                await Shipping.number_of_devices.set()

                async with state.proxy() as data:
                    data["time"] = time.strftime("%H:%M")

                await message.answer("Сколько приборов потребуется?",
                                     parse_mode=types.ParseMode.HTML)
    except Exception as _ex:
        if str(_ex) == 'time error':
            text = f"К сожалению время не вернуть назад 😢 Введите корректное время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ. Сейчас {datetime.now().time().strftime('%H:%M')}"
        else:
            text = f"Я Вас, к сожалению, не понимаю. Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ. Сейчас {datetime.now().time().strftime('%H:%M')}"

        await message.answer(text=text)
        return


@dp.message_handler(content_types=["text"], state=Shipping.number_of_devices)
async def shipping_number_of_devices(message: types.Message, state: FSMContext):
    """Ловлю от пользователя количество приборов"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка кол-во приборров')
    if message.text.isdigit():
        await Shipping.phone.set()
        async with state.proxy() as data:
            data['number_of_devices'] = message.text

        text = "Введите или отправьте Ваш контактный номер телефона "
        msg = await message.answer(text=text, reply_markup=send_phone)
    else:
        text = "К сожалению я Вас не понимаю, введите корректные данные!!! \nСколько приборов потребуется?"
        await message.answer(text=text)


@dp.message_handler(content_types=["contact", "text"], state=Shipping.phone)
async def shipping_address(message: types.Message, state: FSMContext):
    """Ловлю от пользователя контактный номер телефона"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка номер телефона')
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
    await Shipping.address.set()

    text = "Укажите адрес на который нужно доставить"
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types=["text"], state=Shipping.address)
async def shipping_address(message: types.Message, state: FSMContext):
    """Ловлю от пользователя адрес доставки"""
    await db.update_last_activity(user_id=message.from_user.id, button='Доставка адрес доставки')
    await Shipping.pay_method.set()

    async with state.proxy() as data:
        data['address'] = message.text

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="💳 Карта", callback_data="pay_method_card"),
        InlineKeyboardButton(text="💵 Наличка", callback_data="pay_method_money"),
    )
    await message.answer(text="Выберите способ оплаты", reply_markup=markup)


@dp.callback_query_handler(text=["pay_method_card", "pay_method_money"], state=Shipping.pay_method)
async def shipping_pay_method(call: types.CallbackQuery, state: FSMContext):
    """Ловлю от пользователя способ оплаты"""
    await db.update_last_activity(user_id=call.message.from_user.id, button='Доставка сопособ оплаты')
    await Shipping.check.set()
    await call.message.edit_reply_markup(reply_markup="")
    await call.message.delete()
    cart_info = await db.cart_info(user_id=str(call.message.chat.id))

    text = "Ваш заказ\n"
    summa = 0
    item_list = []
    for item in cart_info:
        item_list.append(
            {
                "title": item['title'],
                'count': item['item_count'],
                'price': int(item['price'])
            }
        )
        text += f"{item['title']}\nКол-во порций: {item['item_count']}\nЦена: {item['price']}\n\n"
        summa += item['item_count'] * item['price']

    async with state.proxy() as data:
        data['items'] = item_list
        data['pay_method'] = call.data
        data['final_summa'] = summa

    text += f"Общая сумма заказа: {summa}"

    await call.message.answer(text=text, reply_markup=user_inline_approve)


@dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"], state=Shipping.check)
async def shipping_user_check_data(call: types.CallbackQuery, state: FSMContext):
    """Ловлю от пользователя проверку данных"""
    await db.update_last_activity(user_id=call.message.from_user.id, button='Доставка проверка данных')
    await call.message.edit_reply_markup(reply_markup="")
    await call.message.delete()
    await call.answer(cache_time=10)

    if call.data == "approve_order_user":
        data = await state.get_data()

        json_data = json.dumps(data['items'])

        user_id = call.message.chat.id
        await db.delete_cart(user_id=str(user_id))

        order_id = await db.add_new_shipping_order(
            tpc=json_data,
            number_of_devices=int(data['number_of_devices']),
            address=data['address'], phone=data['phone_number'], data_reservation=data['data'],
            time_reservation=data['time'], final_summa=data['final_summa'], pay_method=data['pay_method'],
            user_id=str(data['user_id']),
            user_name=data['user_name']
        )
        text = f"{data['user_name']} Ваша заявка отправлена нашему сотруднику. Ожидайте. Он с Вами скоро свяжется"
        await call.message.answer(text=text, reply_markup=menuUser)

        text = "Поступила заявка на доставку\n"
        text += f"Пользователь @{data['user_name']} заказал:\n"
        for item in data['items']:
            text += f"{item['title']} - {item['count']}\n"
        text += "-" * 70 + "\n"
        text += f"Количество приборов: {data['number_of_devices']}\n"
        text += f"Дата доставки: {data['data']}\n"
        text += f"Время доставки: {data['time']}\n"
        text += f"Адрес доставки: {data['address']}\n"
        if data['pay_method'] == "pay_method_card":
            text += "Способ оплаты: Карта\n"
        elif data['pay_method'] == "pay_method_money":
            text += "Способ оплаты: Наличные\n"
        text += f"Контактный номер телефона: {data['phone_number']}\n"
        text += "-" * 70 + "\n"
        text += f"<b>Сумма заказа: {data['final_summa']}</b>\n"

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton(text="Взять в работу", callback_data=f"admin_approve_shipping-{order_id}-"),
            InlineKeyboardButton(text="Отмена", callback_data=f"admin_cancel_shipping-{order_id}")
        )
        markup.row(
            InlineKeyboardButton("Написать гостю в ЛС", callback_data=f"shipping_write_to_pm-{order_id}",
                                 url=f"https://t.me/{data['user_name']}")
        )

        await bot.send_message(chat_id=admins[0], text=text, parse_mode="HTML", reply_markup=markup)
        await state.finish()

    elif call.data == "cancel_order_user":
        user_id = call.message.chat.id
        await db.delete_cart(user_id=str(user_id))

        await state.finish()
        text = "Главное меню"
        await call.message.answer(text=text, reply_markup=menuUser)


@dp.callback_query_handler(text_contains=["shipping"])
async def shipping_admin_check_order(call: types.CallbackQuery, state: FSMContext):
    """Ловлю от администратора ответ о заявке"""
    ikb = call.message.reply_markup.inline_keyboard.copy()
    ikb.pop(0)
    markup = InlineKeyboardMarkup()
    markup.add(ikb[0][0])
    await call.message.edit_reply_markup(reply_markup=markup)
    data = call.data.split('-')

    await db.update_shipping_order_status(id=int(data[1]), admin_name=call.from_user.username,
                                          admin_id=str(call.from_user.id), admin_answer=data[0])
