from keyboards.default.menu import menuCategories
from loader import dp, bot

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext


# Отмена действия
@dp.message_handler(Text("Назад"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()

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
    await message.answer(f"Меню вызова персонала ниже", reply_markup=menuPersonal)


@dp.message_handler(Text(equals=["Меню"]))
async def menu(message:Message):
    text = f"Выберите что Вы хотите"
    await message.answer(text, reply_markup=menuCategories)

@dp.message_handler(Text(equals=["Горячее"]))
async def menu(message:Message):
    text = f"https://teletype.in/@andreytikhonov/R_FmFE6nWVn"
    await message.answer(text)

@dp.message_handler(Text(equals=["Завтраки"]))
async def menu(message:Message):
    text = f"https://teletype.in/@andreytikhonov/1UFRX0WmR"
    await message.answer(text)


@dp.message_handler(Text(equals=["О нас"]))
async def menu(message:Message):
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)
