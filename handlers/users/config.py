from datetime import datetime, timezone

from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.menu import menuUser, menuAdmin, cancel_btn, menu_admin_config
from aiogram.dispatcher import FSMContext
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from states.config import ConfigAdmins, ConfigBlackList
from data.config import admins

db = DBCommands()


async def build_admins_keyboard(users, action):
    """Построение клавиатуры администраторов"""
    markup = InlineKeyboardMarkup()

    button_text = ""
    cb_prefix1 = ""
    cb_prefix2 = ""
    cb_prefix3 = ""

    if action == "admins":
        button_text = "Добавить нового администротора"
        cb_prefix1 = "admin-show"
        cb_prefix2 = "admin-delete"
        cb_prefix3 = "new_admin"

    elif action == "blacklist":
        button_text = ""
        cb_prefix1 = "user-show"
        cb_prefix2 = "user-unblock"
        cb_prefix3 = "ban_user"

    for user in users:
        markup.add(
            InlineKeyboardButton(
                text=f"{user['username']}",
                callback_data=f"{cb_prefix1}-{str(user['id'])}"),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"{cb_prefix2}-{str(user['id'])}")
        )
    markup.row(
        InlineKeyboardButton(
            text=f"{button_text}", callback_data=cb_prefix3)
    )
    return markup


@dp.message_handler(Text(contains="Администраторы бота"), state=ConfigAdmins.config_main)
async def config_username_for_admin(message: types.Message, state=FSMContext):
    """Ловлю нажатие на кнопку Администраторы бота"""
    await ConfigAdmins.config_admins_list.set()
    id_msg_list = []
    text = "Здесь Вы можете добавити/удалить администратора"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    id_msg_list.append(msg.message_id)

    admins = await db.get_all_admins()
    markup = await build_admins_keyboard(users=admins, action='admins')

    msg = await message.answer(text='Администроторы', reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(text_contains=["admin-delete"], state=ConfigAdmins.config_admins_list)
async def remove_admin_status(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку удаление администратора"""
    user_id = call.data.split("-")[-1]
    data = await state.get_data()
    try:
        await db.remove_admin_status_from_user(id=int(user_id))
    except Exception as _ex:
        pass

    admins = await db.get_all_admins()
    markup = await build_admins_keyboard(users=admins, action='admins')

    msg = await call.message.edit_reply_markup(reply_markup=markup)


@dp.callback_query_handler(text_contains=["new_admin"], state=ConfigAdmins.config_admins_list)
async def add_admin_status(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку добавление администратора """
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
    """Ловлю username от пользователя для удаления пользователя из администраторов"""
    username = message.text.strip()
    data = await state.get_data()
    id_msg_list = data['id_msg_list']

    try:
        await db.add_admin_status_for_user(username=username)
    except Exception as _ex:
        await message.answer(text=f"Пользователя {username} нет в нашей базе данных пользователей",
                             reply_markup=menu_admin_config)
        await state.finish()
        await ConfigAdmins.config_main.set()

    admins = await db.get_all_admins()
    markup = await build_admins_keyboard(users=admins, action='admins')

    msg = await message.answer(text='Администроторы', reply_markup=markup)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains="Список нарушителей"), state=ConfigAdmins.config_main)
async def config_blacklist(message: types.Message, state=FSMContext):
    """Ловлю нажатие на кнопку Список нарушителей и вывожу инлайн список с нарушителями"""
    await ConfigBlackList.config_blacklist.set()

    id_msg_list = []
    text = "Здесь Вы можете добавити/удалить нарушителя"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    id_msg_list.append(msg.message_id)

    violators = await db.get_black_list()
    markup = await build_admins_keyboard(users=violators, action='blacklist')

    msg = await message.answer(text='Нарушители', reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(text_contains=["user-unblock"], state=ConfigBlackList.config_blacklist)
async def unban_user(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку удаления статуса Забанен"""
    user_id = call.data.split("-")[-1]
    data = await state.get_data()

    try:
        await db.update_blacklist_status(id=int(user_id), reason="-", status=False)
    except Exception as _ex:
        print(_ex)

    violators = await db.get_black_list()
    if violators:
        markup = await build_admins_keyboard(users=violators, action='blacklist')
        msg = await call.message.edit_reply_markup(reply_markup=markup)


