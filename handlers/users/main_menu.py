from loader import dp, bot

from aiogram import types
from keyboards.default import *
from keyboards.inline import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.config import MainMenu
from states.shipping import Shipping


# Отмена действия
@dp.message_handler(Text("Назад"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    await message.delete()

    if message.from_user.id == int(admins[0]):
        await message.answer("Главное меню", reply_markup=menuUser)

    else:
        await message.answer("Главное меню", reply_markup=menuUser)

    if current_state == "MainMenu:main":
        if data != {}:
            await bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
        else:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id-1)
    await state.finish()


@dp.message_handler(Text(equals=["Вызов персонала"]))
async def ansver_menu(message: Message):
    text = f"Меню вызова персонала ниже"
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(equals=["Меню"]))
async def menu(message: Message):

    text = f"Меню к Вашим услугам"
    markup = await show_menu_buttons(message_id=message.message_id+1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.message_handler(Text(equals=["О нас"]))
async def menu(message: Message):
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


@dp.message_handler(Text("Доставка"), state=None)
async def shipping_in(message: types.Message, state: FSMContext):
    await Shipping.title_item.set()

    # text = f""
    text = f"""\n
    1️⃣ Название блюда (если оно не одно, то ввести через запятую)\n
    2️⃣ Количество порций (если блюдо не одно, то ввести через запятую, в том порядке что и названия блюд)\n
    3️⃣ Количество персон\n
    4️⃣ Дата доставки\n
    5️⃣ Время доставки\n
    6️⃣ Адресс доставки\n
    7️⃣ Контактный телефон\n\n
    <b>Шаг [1/7]</b> Введите название блюда
"""
    await message.answer(text=text, reply_markup=cancel_btn)

# Административная часть
@dp.message_handler(Text(equals=["Настройки"]), state="*")
async def admin_config(message: Message):
    text = "Меню настроек"
    await MainMenu.main.set()
    await message.answer(text=text, reply_markup=menu_admin_config)
