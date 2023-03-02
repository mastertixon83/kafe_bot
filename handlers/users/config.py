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


async def build_admins_keyboard():
    """Построение клавиатуры администраторов"""
    markup = InlineKeyboardMarkup()
    admins = await db.get_all_admins()

    for user in admins:
        markup.add(
            InlineKeyboardButton(
                text=f"{user['username']}",
                callback_data=f"admin-show-{str(user['id'])}"),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"admin-delete-{str(user['id'])}")
        )
    markup.row(
        InlineKeyboardButton(
            text="Добавить нового администротора", callback_data="new_admin")
    )
    return markup


@dp.message_handler(Text(contains="Администраторы бота"), state="*")
async def config_username_for_admin(message: types.Message, state=FSMContext):
    await ConfigAdmins.config_admins_list.set()
    id_msg_list = []
    text = "Здесь Вы можете добавити/удалить администратора"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    id_msg_list.append(msg.message_id)

    markup = await build_admins_keyboard()

    msg = await message.answer(text='Администроторы', reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


### Удаление пользователя из администраторов
@dp.callback_query_handler(text_contains=["admin-delete"], state="*")
async def remove_admin_status(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split("-")[-1]
    data = await state.get_data()
    await db.remove_admin_status_from_user(id=int(user_id))

    markup = await build_admins_keyboard()

    msg = await call.message.edit_reply_markup(reply_markup=markup)


@dp.callback_query_handler(text_contains=["new_admin"], state="*")
async def add_admin_status(call: types.CallbackQuery, state: FSMContext):
    """Добавление администратора"""
    await ConfigAdmins.config_admins_name.set()
    data = await state.get_data()

    text = "Введи username пользователя (Пользователь должен быть подписан на бота)"
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data['id_msg_list'][-1])

    id_msg_list = data['id_msg_list']
    msg = await call.message.answer(text=text)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(content_types=["text"], state=ConfigAdmins.config_admins_name)
async def username_for_admin(message: types.Message, state: FSMContext):
    """Ловлю username от пользователя"""
    username = message.text
    data = await state.get_data()
    id_msg_list = data['id_msg_list']

    await db.add_admin_status_for_user(username=username)

    markup = await build_admins_keyboard()

    msg = await message.answer(text='Администроторы', reply_markup=markup)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list

    await ConfigAdmins.config_admins_list.set()


