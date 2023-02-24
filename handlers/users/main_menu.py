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
@dp.message_handler(Text(contains="Назад"), state="*")
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
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id-1)
    await state.finish()


@dp.message_handler(Text(contains=["Вызов персонала"]))
async def ansver_menu(message: Message):
    text = f"Меню вызова персонала ниже"
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.message_handler(Text(contains=["Меню"]))
async def menu(message: Message):

    text = f"Меню к Твоим услугам"
    markup = await show_menu_buttons(message_id=message.message_id+1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.message_handler(Text(contains=["О ресторане"]))
async def menu(message: Message):
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


@dp.message_handler(Text(contains="Оформить заказ на доставку"), state=None)
async def shipping_in(message: types.Message, state: FSMContext):
    await Shipping.title_item.set()

    text = f"<b>Шаг [1/8]</b> Введи название блюда (если блюд несколько, то введи через запятую)"
    await message.answer(text=text, reply_markup=cancel_btn)

# Административная часть
@dp.message_handler(Text(contains=["Настройки"]), state="*")
async def admin_config(message: Message):
    text = "Меню настроек"
    await MainMenu.main.set()
    await message.answer(text=text, reply_markup=menu_admin_config)
