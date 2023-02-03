from loader import dp

from aiogram.types import Message
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext


# Отмена действия
@dp.message_handler(Text("Назад"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    await message.delete()
    if message.from_user.id == int(admins[0]):
        await message.answer("Главное меню", reply_markup=menuUser)

    else:
        await message.answer("Главное меню", reply_markup=menuUser)

    if current_state is None:
        pass
    else:
        await state.finish()


@dp.message_handler(Text(equals=["Вызов персонала"]))
async def ansver_menu(message: Message):
    await message.delete()
    text = f"Меню вызова персонала ниже"
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(equals=["Меню"]))
async def menu(message: Message):
    await message.delete()
    text = f"Выберите что Вы хотите"
    await message.answer(text, reply_markup=menuCategories)


@dp.message_handler(Text(equals=["Горячее"]))
async def menu(message: Message):
    await message.delete()
    text = f"https://teletype.in/@andreytikhonov/R_FmFE6nWVn"
    await message.answer(text)


@dp.message_handler(Text(equals=["Завтраки"]))
async def menu(message: Message):
    await message.delete()
    text = f"https://teletype.in/@andreytikhonov/1UFRX0WmR"
    await message.answer(text)


@dp.message_handler(Text(equals=["О нас"]))
async def menu(message: Message):
    await message.delete()
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


# Административная часть
@dp.message_handler(Text(equals=["Настройки"]))
async def admin_config(message: Message):
    text = "Меню настроек"
    await message.answer(text=text, reply_markup=menu_admin_config)


@dp.message_handler(Text(equals=["Редактировать меню"]))
async def admin_config_menu_edit(message: Message):
    text = "Редактирование меню"

    await message.answer(text=text, reply_markup=menu_admin_edit)