# #TODO: Админская часть вывод заявок на доставку по датам
# from datetime import datetime, timezone
#
# from aiogram.dispatcher import FSMContext
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
#
# from loader import dp, bot, db
# from aiogram import types
#
# from keyboards.inline.inline_buttons import admin_inline_staff, admin_inline_send_ls, \
#     user_inline_approve, admin_inline_shipping_order
#
# from keyboards.default.menu import menuUser, menuAdmin, \
#     send_phone_cancel, cancel_btn
#
# from states.shipping import Shipping
# from utils.db_api.db_commands import DBCommands
#
# from aiogram.dispatcher.filters import Text
# from data.config import admins
#
# db = DBCommands()
#
#
# ### Ловлю от пользователя название блюда
# @dp.message_handler(content_types=["text"], state=Shipping.title_item)
# async def shipping_title(message: types.Message, state: FSMContext):
#     await Shipping.portion_quantity.set()
#
#     async with state.proxy() as data:
#         data['title'] = message.text
#         data['user_name'] = message.from_user.username
#         data['user_id'] = message.from_user.id
#
#     text = "<b>Шаг [2/8]</b> Введи количество порций (если блюда не одно, то введи через запятую в том порядке что и названия блюд)"
#     await message.answer(text=text, reply_markup=cancel_btn)
#
#
# ### Ловлю от пользователя количество порций
# @dp.message_handler(content_types=["text"], state=Shipping.portion_quantity)
# async def shipping_portion_quantity(message: types.Message, state: FSMContext):
#     if message.text.isdigit():
#         await Shipping.number_of_devices.set()
#
#         async with state.proxy() as data:
#             data['portion_quantity'] = message.text
#
#         text = "<b>Шаг [3/8]</b> Сколько приборов потребуется?"
#         await message.answer(text=text, reply_markup=cancel_btn)
#     else:
#         text = "Я Тебя не понимаю, введи корректные данные!!! \n <b>Шаг [2/8]</b> Введи количество порций (если блюда не одно, то введи через запятую в том порядке что и названия блюд)"
#         await message.answer(text=text, reply_markup=cancel_btn)
#
#
# ### Ловлю от пользователя количество приборов
# @dp.message_handler(content_types=["text"], state=Shipping.number_of_devices)
# async def shipping_number_of_devices(message: types.Message, state: FSMContext):
#     if message.text.isdigit():
#         await Shipping.data.set()
#         async with state.proxy() as data:
#             data['number_of_devices'] = message.text
#
#         date = datetime.now().strftime('%d.%m.%Y').split('.')
#         text = "<b>Шаг [4/8]</b> На какую дату оформить доставку?\n"
#         text += f"Введите дату в формате ДД.ММ.ГГГГ \n Сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"
#         await message.answer(text=text, reply_markup=cancel_btn)
#     else:
#         text = "К сожалению я Тебя не понимаю, введи корректные данные!!! \n <b>Шаг [3/8]</b> Сколько приборов потребуется?"
#         await message.answer(text=text, reply_markup=cancel_btn)
#
#
# ### Ловлю от пользователя дату доставки
# @dp.message_handler(content_types=["text"], state=Shipping.data)
# async def shipping_number_of_devices(message: types.Message, state: FSMContext):
#     try:
#         date = message.text
#         if len(date.split('.')) == 3:
#             if (len(date.split('.')[0]) == 2) and (len(date.split('.')[1]) == 2) and (len(date.split('.')[2]) == 4):
#                 if datetime.strptime(date, "%d.%m.%Y") < datetime.now():
#                     raise Exception('data error')
#                 else:
#                     async with state.proxy() as data:
#                         data["data"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()
#
#                     await Shipping.time.set()
#
#                     text = "<b>Шаг [5/8]</b>\n\n К какому времени доствить? Введи время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
#                     await message.answer(text, parse_mode=types.ParseMode.HTML)
#         else:
#             raise Exception("input error")
#     except Exception as _ex:
#         if (str(_ex) == 'input error') or (str(_ex) == 'day is out of range for month'):
#             text = f"<b>Шаг [5/8]</b>\n\nК сожалению я Тебя не понимаю, введит корректную дату в правильном формате ДД.ММ.ГГГГ, сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"
#
#         elif str(_ex) == 'data error':
#             #К сожалению время не вернуть назад, укажите корректную дату, сегодня 24.02.2023
#             text = f"<b>Шаг [5/8]</b>\n\nК сожалению время не вернуть назад 😢 Введи корректную дату в формате ДД.ММ.ГГГГ, сегодня {datetime.strftime(datetime.now(), '%d.%m.%Y')}"
#
#         text = ""
#         await message.answer(text=text)
#         return
#
#
# ### Ловлю от пользователя время доставки
# @dp.message_handler(content_types=["text"], state=Shipping.time)
# async def shipping_time(message: types.Message, state: FSMContext):
#     msg = message.text
#     data = await state.get_data()
#     try:
#         if len(msg) == 5:
#             if " " in msg:
#                 msg = msg.replace(" ", ":")
#             elif "." in msg:
#                 msg = msg.replace(".", ":")
#             elif "-" in msg:
#                 msg = msg.replace("-", ":")
#
#             msg = msg + ":00"
#
#             time = datetime.strptime(msg, '%H:%M:%S').time()
#             if data['data'] == datetime.now() and time < datetime.now().time():
#                 raise Exception('time error')
#             else:
#                 await Shipping.address.set()
#
#                 async with state.proxy() as data:
#                     data["time"] = time.strftime("%H:%M:%S")
#
#                 await message.answer("<b>Шаг [6/8]</b> Введи адрес доставки",
#                                      parse_mode=types.ParseMode.HTML)
#     except Exception as _ex:
#         if str(_ex) == 'time error':
#             text = "К сожалению время не вернуть назад 😢 Введи корректное время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
#         else:
#             text = "Я Тебя, к сожалению, не понимаю. Введи время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ"
#
#         await message.answer(text=text)
#         return
#
#
# ### Ловлю от пользователя адресс доставки
# @dp.message_handler(content_types=["text"], state=Shipping.address)
# async def shipping_time(message: types.Message, state: FSMContext):
#     await Shipping.phone.set()
#
#     text = "<b>Шаг [7/8]</b> Введи или отправь Свой контактный номер телефона "
#     msg = await message.answer(text=text, reply_markup=send_phone_cancel)
#
#     async with state.proxy() as data:
#         data['address'] = message.text
#         data['message_id'] = msg.message_id
#
#
# ### Ловлю от пользователя номер телефона
# @dp.message_handler(content_types=["contact", "text"], state=Shipping.phone)
# async def shipping_time(message: types.Message, state: FSMContext):
#     await Shipping.pay_method.set()
#
#     async with state.proxy() as data:
#         if message.content_type == 'contact':
#             if message.contact.phone_number[0] != "+":
#                 data["phone_number"] = "+" + message.contact.phone_number
#             else:
#                 data["phone_number"] = message.contact.phone_number
#             data["name"] = message.contact.last_name
#         else:
#             data["phone_number"] = message.text
#             data["name"] = message.from_user.username
#
#     text = "<b>Шаг [8/8]</b> 💳 vs 💵"
#     msg = await message.answer(text=text, reply_markup=cancel_btn)
#     markup = InlineKeyboardMarkup()
#     markup.add(
#         InlineKeyboardButton(text="💳 Карта", callback_data="pay_method_card"),
#         InlineKeyboardButton(text="💵 Наличка", callback_data="pay_method_money"),
#     )
#     await message.answer(text="Выбери способ оплаты", reply_markup=markup)
#
#
# ### Ловлю ответ от пользователя способ оплаты
# @dp.callback_query_handler(text=["pay_method_card", "pay_method_money"], state=Shipping.pay_method)
# async def shipping_pay_method(call: types.CallbackQuery, state: FSMContext):
#     await Shipping.check.set()
#
#     await call.message.edit_reply_markup(reply_markup="")
#
#     async with state.proxy() as data:
#         data['pay_method'] = call.data
#
#     text = f"""{data['name']}, Твой заказ\n
#     1️⃣ {data['title']}\n
#     2️⃣ {data['portion_quantity']}\n
#     3️⃣ {data['number_of_devices']}\n
#     4️⃣ {data['data']}\n
#     5️⃣ {data['time']}\n
#     6️⃣ {data['address']}\n
#     7️⃣ {data['pay_method']}\n
#     8️⃣ {data['phone_number']}\n
#     Если всё правильно, подтверди
# """
#     await call.message.answer(text=text, reply_markup=user_inline_approve)
#
#
# ### Ловлю ответ от пользователя о проверке данных
# @dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"], state=Shipping.check)
# async def shipping_user_check_data(call: types.CallbackQuery, state: FSMContext):
#     await call.message.edit_reply_markup(reply_markup="")
#     await call.message.delete()
#
#     await call.answer(cache_time=60)
#
#     if call.data == "approve_order_user":
#         data = await state.get_data()
#
#         order_id = await db.add_new_shipping_order(
#             title=data['title'], portion_quantity=int(data['portion_quantity']),
#             number_of_devices=int(data['number_of_devices']),
#             address=data['address'], phone=data['phone_number'], data_reservation=data['data'],
#             time_reservation=data['time'][:-3], pay_method=data['pay_method'], user_id=str(data['user_id']),
#             user_name=data['user_name']
#         )
#         text = f"{data['user_name']} Твоя заявка отправлена нашему сотруднику. Ожидай. Он с Тобой скоро свяжется"
#         await call.message.answer(text=text, reply_markup=menuUser)
#         text = "Поступила заявка на доставку\n"
#         text += f"Пользователь @{data['user_name']} заказал:\n"
#         text += f"{data['title']}\n"
#         text += f"Количество порций: {data['portion_quantity']}\n"
#         text += f"Количество приборов: {data['number_of_devices']}\n"
#         text += f"Дата доставки: {data['data']}\n"
#         text += f"Время доставки: {data['time']}\n"
#         text += f"Адрес доставки: {data['address']}\n"
#         if data['pay_method'] == "pay_method_card":
#             text += "Способ оплаты: Карта\n"
#         elif data['pay_method'] == "pay_method_money":
#             text += "Способ оплаты: Наличные\n"
#         text += f"Контактный номер телефона: {data['phone_number']}\n"
#
#         markup = InlineKeyboardMarkup()
#
#         markup.add(
#             InlineKeyboardButton(text="Взять в работу", callback_data=f"admin_approve_shipping-{order_id}"),
#             InlineKeyboardButton(text="Отмена", callback_data=f"admin_cancel_shipping-{order_id}")
#         )
#         markup.row(
#             InlineKeyboardButton("Написать гостю в ЛС", callback_data=f"shipping_write_to_pm-{order_id}",
#                                  url=f"https://t.me/{data['user_name']}")
#         )
#
#         await bot.send_message(chat_id=admins[0], text=text, reply_markup=markup)
#         await state.finish()
#
#     elif call.data == "cancel_order_user":
#         await Shipping.title_item.set()
#         text = f"<b>Шаг [1/8]</b> Введи название блюда (если блюд несколько, то введи через запятую)"
#         await call.message.answer(text=text, reply_markup=cancel_btn)
#
#
# ### Ловлю ответ от администратора о заявке
# # @dp.callback_query_handler(text_contains=["shipping"])
# # async def shipping_admin_check_order(call: types.CallbackQuery):
# #     await call.message.edit_reply_markup(reply_markup="")
# #     data = call.data.split('-')
# #
# #     await db.update_shipping_order_status(id=int(data[1]), admin_name=call.from_user.username,
# #                                             admin_id=str(call.from_user.id), admin_answer=data[0])
#
