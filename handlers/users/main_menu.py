from loader import dp, bot
import re
from datetime import datetime

from aiogram import types
from keyboards.default import *
from keyboards.inline import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.config import ConfigAdmins
from states.mailings import Mailings


# Отмена действия
@dp.message_handler(Text(contains="Главное меню"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    await message.delete()

    if message.from_user.id == int(admins[0]):
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
        for id_msg in data['id_msg_list']:
            try:
                await bot.delete_message(chat_id=message.from_user.id, message_id=id_msg)
            except Exception as ex:
                pass

    await state.finish()
    await db.delete_cart(str(message.chat.id))


@dp.message_handler(Text(contains=["Вызов персонала"]))
async def ansver_menu(message: Message):
    text = f"Меню вызова персонала ниже"
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(contains=["Меню"]))
async def menu(message: Message):
    text = f"Меню к Твоим услугам"
    msg = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

    markup = await show_menu_buttons(message_id=msg.message_id + 1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.message_handler(Text(contains=["О ресторане"]))
async def menu(message: Message):
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


@dp.message_handler(Text(contains=["Настройки"]), state="*")
async def admin_config(message: Message):
    text = "Меню настроек"
    await ConfigAdmins.config_main.set()
    await message.answer(text=text, reply_markup=menu_admin_config)


@dp.message_handler(Text(contains="Сделать рассылку подписчикам"), state="*")
async def newsletter(message: Message):
    """Лювлю нажатие на кнопку Сделать рассылку пользователям"""
    text = "Меню рассылки"
    await Mailings.main.set()
    await message.answer(text=text, reply_markup=newsletter_kbd)
