from datetime import datetime, timezone

from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.menu import menuUser, menuAdmin, cancel_btn
from aiogram.dispatcher import FSMContext
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from states.config import ConfigAdmins
from data.config import admins

db = DBCommands()


@dp.message_handler(Text(contains="Администраторы бота"), state = "*")
async def config_username_for_admin(message: types.Message):
    await ConfigAdmins.config_admins_name.set()

    admins = await db.get_all_admins()

    markup = InlineKeyboardMarkup()

    for user in admins:
        markup.add(
            InlineKeyboardButton(
                text=f"{user['username']}",
                callback_data=f"user_id-{str(user['id'])}-show"),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"user_id-{str(user['id'])}-delete")
        )
        markup.row(
            InlineKeyboardButton(
                text="Добавит нового администротора", callback_data="new_admin")
        )

    await message.answer(text='Администроторы', reply_markup=markup)