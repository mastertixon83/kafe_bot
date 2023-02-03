from loader import dp, bot
from data.config import admins
from utils.db_api.db_commands import DBCommands

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

db = DBCommands()


# Редактирование категорий
@dp.message_handler(Text("Категории"))
async def admin_edit_categories(message: Message):
    text = "Редактирование категорий"
    await message.answer(text=text)
    categories = await db.get_all_categories()

    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке

    for category in categories:
        markup.inline_keyboard.clear()
        row = [
            InlineKeyboardButton("Редактировать", callback_data=f"edit-{str(category['id'])}"),
            InlineKeyboardButton("Удалить", callback_data=f"delete-{str(category['id'])}")
        ]
        markup.add().row(*row)
        await message.answer(text=f"{str(category['title'])}", reply_markup=markup)

