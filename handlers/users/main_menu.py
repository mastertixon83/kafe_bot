from loader import dp

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

    if current_state is None:
        if message.from_user.id == int(admins[0]):
            await message.answer("Главное меню", reply_markup=menuUser)
        else:
            await message.answer("Главное меню", reply_markup=menuUser)
    else:
        await state.finish()
        if message.from_user.id == int(admins[0]):
            await message.answer("Главное меню", reply_markup=menuUser)
        else:
            await message.answer("Главное меню", reply_markup=menuUser)


@dp.message_handler(Text(equals=["Вызов персонала"]))
async def ansver_menu(message: Message):
    await message.answer(f"Меню вызова персонала ниже", reply_markup=menuPersonal)


@dp.message_handler(Text(equals=["Программа лояльности"]))
async def program_loyality(message: Message):
    await message.answer("Меню программы лояльности ниже", reply_markup=menuLoyality)
