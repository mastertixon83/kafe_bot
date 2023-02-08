from loader import dp, bot

from aiogram.types import Message
from aiogram import types
from keyboards.default import *
from keyboards.inline import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.config import MainMenu


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

    if current_state is None:
        pass
    else:
        if current_state == "MainMenu:main":
            await bot.delete_message(chat_id=data['chat_id'], message_id=int(data['message_id']))
        await state.finish()


@dp.message_handler(Text(equals=["Вызов персонала"]))
async def ansver_menu(message: Message):
    text = f"Меню вызова персонала ниже"
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(equals=["Меню"]))
async def menu(message: Message):
    await message.delete()
    text = f"Выберите что Вы хотите"
    markup = await show_menu_buttons()
    await message.answer(text=text, reply_markup=markup)


@dp.message_handler(Text(equals=["О нас"]))
async def menu(message: Message):
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


# Административная часть
@dp.message_handler(Text(equals=["Настройки"]))
async def admin_config(message: Message):
    text = "Меню настроек"
    await MainMenu.main.set()
    await message.answer(text=text, reply_markup=menu_admin_config)
