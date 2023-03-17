from handlers.users.user_order_shipping import build_category_keyboard
from loader import dp, bot
import re
from datetime import datetime

from aiogram import types
from keyboards.default import *
from keyboards.inline import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.config import ConfigAdmins, MainMenu
from states.mailings import Mailings
from states.restoran import TableReservation


# Отмена действия
@dp.message_handler(Text(contains="Главное меню"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()

    data = await state.get_data()
    await message.delete()

    if str(message.from_user.id) == admins[0]:
        await message.answer("Главное меню", reply_markup=menuAdmin)
    else:
        await message.answer("Главное меню", reply_markup=menuUser)

    if current_state == "MainMenu:main":
        if data != {}:
            await bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
        else:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)

    elif (re.search(r"ConfigAdmins:config_admins_", current_state) or re.search(r"ConfigBlackList:config_blacklist",
                                                                                current_state) or re.search(
            r"ConfigAdmins:config_main", current_state) or re.search(r"Mailings", current_state)):
        if data['id_msg_list']:
            for id_msg in data['id_msg_list']:
                try:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=id_msg)
                except Exception as ex:
                    pass

    await state.finish()
    await db.delete_cart(str(message.chat.id))


@dp.message_handler(Text(contains=["О ресторане"]))
async def menu(message: Message):
    """Обработчик нажатия на кнопку О Ресторане"""
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


@dp.message_handler(Text(contains=["Меню"]), state="*")
async def menu(message: Message):
    """Обработчик нажатия на кнопку Меню"""
    text = f"Меню к Твоим услугам"
    msg = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    # await MainMenu.main.set()
    markup = await show_menu_buttons(message_id=msg.message_id + 1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.message_handler(Text(contains=["Вызов персонала"]), state="*")
async def ansver_menu(message: Message):
    """Обработчик нажатия на кнопку вызов персонала"""
    text = f"Меню вызова персонала ниже"
    await MainMenu.main.set()
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(contains="Забронировать стол"), state=None)
async def table_reservation(message: types.Message, state: FSMContext):
    """Обработчик нажатия на кнопку Забронировать стол"""
    await TableReservation.data.set()

    date = datetime.now().strftime('%d.%m.%Y')
    text = f"<b>Шаг [1/5]</b>\n\n Введи дату в формате ДД.ММ.ГГГГ, сегодня {date}"
    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

    async with state.proxy() as data:
        data["chat_id"] = str(message.chat.id)
        data["user_name"] = message.from_user.username
        data["user_id"] = str(message.from_user.id)
        data['full_name'] = message.from_user.full_name


@dp.message_handler(Text(contains="Оформить заказ на доставку"), state=None)
async def show_menu_order_shipping(message: types.Message, state: FSMContext):
    """Обработчик нажатия на кнопку Оформить заказ на доставку"""
    await message.delete()
    await db.delete_cart(str(message.chat.id))
    await message.answer('Оформление заказа на доставку', reply_markup=ReplyKeyboardRemove())
    await build_category_keyboard(message)

    async with state.proxy() as data:
        data["message_id"] = message.message_id + 2
        data["chat_id"] = message.from_user.id


@dp.message_handler(Text(contains="Программа лояльности"), state=None)
async def reg_loyal_card(message: Message, state: FSMContext):
    """Обработчик нажатия на кнопку Программа лояльности"""
    info = await db.get_user_info(message.from_user.id)
    await MainMenu.main.set()
    if info[0]['card_status'] != True:
        text = "Оформи карту скидок!!!"
    else:
        text = "Меню программы лояльности"
    await message.delete()
    await message.answer(text, reply_markup=menuLoyality, parse_mode=types.ParseMode.HTML)


@dp.message_handler(Text(contains="Сделать рассылку подписчикам"), state="*")
async def newsletter(message: Message):
    """Лювлю нажатие на кнопку Сделать рассылку пользователям"""
    text = "Меню рассылки"
    await Mailings.main.set()
    await message.answer(text=text, reply_markup=newsletter_kbd)


@dp.message_handler(Text(contains=["Настройки"]), state="*")
async def admin_config(message: Message, state: FSMContext):
    text = "Меню настроек"
    await ConfigAdmins.config_main.set()
    async with state.proxy() as data:
        data['id_msg_list'] = []
    await message.answer(text=text, reply_markup=menu_admin_config)