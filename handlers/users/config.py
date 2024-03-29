# TODO: Настройка планировщика
import os
from datetime import datetime, timezone

from aiogram.dispatcher import FSMContext

from loader import dp, bot, db, logger
from aiogram import types
from aiogram.utils import exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default.menu import cancel_btn, menu_admin_config
from aiogram.dispatcher import FSMContext
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from states.config import ConfigAdmins, ConfigBlackList
from data.config import admins
import re

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
        last_btn_text = "Добавить администратора"

    elif action == "blacklist":
        button_text = ""
        cb_prefix1 = "user-show"
        cb_prefix2 = "user-unblock"
        cb_prefix3 = "ban_user"
        last_btn_text = "Забанить пользователя"

    for user in users:
        markup.add(
            InlineKeyboardButton(
                text=f"{user['username']}",
                callback_data=f"{cb_prefix1}-{str(user['id'])}-{str(user['user_id'])}"),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"{cb_prefix2}-{str(user['id'])}-{str(user['user_id'])}")
        )
    markup.row(
        InlineKeyboardButton(
            text=last_btn_text, callback_data=cb_prefix3)
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

    administrators = await db.get_all_admins()
    markup = await build_admins_keyboard(users=administrators, action='admins')

    msg = await message.answer(text='Администроторы', reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(text_contains=["admin-delete"], state=ConfigAdmins.config_admins_list)
async def remove_admin_status(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку удаление администратора"""
    user_id = call.data.split("-")[-1]

    try:
        await db.remove_admin_status_from_user(id=user_id)
    except Exception as _ex:
        logger.debug(_ex)

    administrators = await db.get_all_admins()
    main_admin = admins[0]
    admins.clear()
    admins.append(main_admin)

    for admin in administrators:
        admins.append(admin['user_id'])

    markup = await build_admins_keyboard(users=administrators, action='admins')

    await call.message.edit_reply_markup(reply_markup=markup)


@dp.callback_query_handler(text_contains=["new_admin"], state=ConfigAdmins.config_admins_list)
async def add_admin_status(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку добавление администратора """
    await ConfigAdmins.config_admins_name.set()
    data = await state.get_data()

    text = "Введите username пользователя (Пользователь должен быть подписан на бота)"
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data['id_msg_list'][-1])

    id_msg_list = data['id_msg_list']
    msg = await call.message.answer(text=text)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(content_types=["text"], state=ConfigAdmins.config_admins_name)
async def username_for_admin(message: types.Message, state: FSMContext):
    """Ловлю username от пользователя для добавления пользователя в администраторы"""
    username = message.text.strip()
    data = await state.get_data()
    id_msg_list = data['id_msg_list']

    try:
        user_id = await db.add_admin_status_for_user(username=username)
        await bot.send_message(
            text="‼️‼️‼️\nВы теперь Администратор, для того чтобы новые права начали действовать, перезапустите бота командой /start",
            chat_id=user_id[0]['user_id'])
    except Exception as _ex:
        msg = await message.answer(text=f"Пользователя {username} нет в нашей базе данных пользователей",
                                   reply_markup=menu_admin_config)
        id_msg_list.append(msg.message_id)
        await state.finish()
        await ConfigAdmins.config_main.set()

    administrators = await db.get_all_admins()
    main_admin = admins[0]
    admins.clear()
    admins.append(main_admin)
    for admin in administrators:
        admins.append(admin['user_id'])

    markup = await build_admins_keyboard(users=administrators, action='admins')

    msg = await message.answer(text='Администроторы', reply_markup=markup)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains="Список нарушителей"), state="*")
async def config_blacklist(message: types.Message, state=FSMContext):
    """Ловлю нажатие на кнопку Список нарушителей и вывожу инлайн список с нарушителями"""
    await ConfigBlackList.config_blacklist.set()

    id_msg_list = []
    text = "Здесь Вы можете добавити/удалить нарушителя"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    id_msg_list.append(msg.message_id)

    violators = await db.get_black_list()

    if violators:
        text = "Нарушители"
    else:
        text = "Черный список пуст"
    markup = await build_admins_keyboard(users=violators, action='blacklist')

    msg = await message.answer(text=text, reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(lambda c: re.search(r"(user-show|admin-show)", c.data), state="*")
async def show_user_info(call: types.CallbackQuery, state: FSMContext):
    """Вывод информации по пользователю"""
    query_text = call.data

    user_id = query_text.split('-')[-1]
    info = await db.get_user_info(user_id=user_id)

    text = f"Информация по пользователю {info[0]['username']}\n"
    text += f"Был зарегистрирован: {info[0]['created_at'].strftime('%d.%m.%Y')}\n"
    text += f"Статус: {'Чист' if not info[0]['ban_status'] else 'Забанен'}\n"
    if info[0]['ban_status'] == True:
        text += f"Причина бана: {info[0]['reason_for_ban']}\n"
    text += f"Номер карточки: {info[0]['card_number']}\n"
    text += f"Статус карточки: {'не активирована' if not info[0]['card_status'] else 'активирована'}\n"
    try:
        count = await db.get_all_invited_users(referral=info[0]['referral_id'])
        text += f"Привел клиентов: {len(count)}"
    except Exception as _ex:
        logger.error(_ex)

    await bot.answer_callback_query(call.id, text=text, show_alert=True)


@dp.callback_query_handler(text_contains=["user-unblock"], state=ConfigBlackList.config_blacklist)
async def unban_user(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку удаления статуса Забанен"""
    user_id = call.data.split("-")[-2]
    data = await state.get_data()
    ban_date = datetime.now()
    try:
        await db.update_blacklist_status(id=int(user_id), reason="-", ban_date=ban_date, status=False)
    except Exception as _ex:
        logger.error(_ex)

    violators = await db.get_black_list()

    if violators:
        text = "Нарушители"
    else:
        text = "Черный список пуст"

    markup = await build_admins_keyboard(users=violators, action='blacklist')
    id_msg_list = data['id_msg_list']

    msg = await call.message.edit_text(text=text, reply_markup=markup)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(text_contains=["ban_user"], state=ConfigBlackList.config_blacklist)
async def ban_user(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на инлайн кнопку Добавит пользователя в черный список"""
    data = await state.get_data()

    await ConfigBlackList.config_blacklist_username.set()

    text = "Введите username пользователя (Пользователь должен быть подписан на бота)"
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data['id_msg_list'][-1])

    id_msg_list = data['id_msg_list']
    del id_msg_list[-1]
    msg = await call.message.answer(text=text)

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(content_types=["text"], state=ConfigBlackList.config_blacklist_username)
async def username_for_ban(message: types.Message, state: FSMContext):
    """Ловлю username от пользователя для добавления пользователя в черный список"""
    await message.delete()
    await ConfigBlackList.config_blacklist_ban_reason.set()

    username = message.text.strip()
    data = await state.get_data()

    id_msg_list = data['id_msg_list']

    msg = await message.answer(text='Введите причину бана')

    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['username'] = username


@dp.message_handler(content_types=["text"], state=ConfigBlackList.config_blacklist_ban_reason)
async def username_ban_reason(message: types.Message, state: FSMContext):
    """Ловлю username от пользователя причину добваления в черный список"""
    await message.delete()
    await ConfigBlackList.config_blacklist.set()

    ban_reason = message.text.strip()

    data = await state.get_data()

    id_msg_list = data['id_msg_list']
    username = data['username']

    user_id = await db.get_user_id(username=username)
    ban_date = datetime.now().date()
    logger.debug(ban_date)
    try:
        await db.update_blacklist_status(id=int(user_id[0]['id']), reason=ban_reason, ban_date=ban_date, status=True)
    except Exception as _ex:
        await message.answer(text=f"Пользователь с username - {username} - в нашей базе данных не найден",
                             reply_markup=cancel_btn)

    for id in id_msg_list:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=id)
        except Exception as _ex:
            logger.error(_ex)

    text = "Здесь Вы можете добавити/удалить нарушителя"
    msg = await message.answer(text=text, reply_markup=cancel_btn)
    id_msg_list.append(msg.message_id)

    violators = await db.get_black_list()

    markup = await build_admins_keyboard(users=violators, action='blacklist')
    msg = await message.answer(text="Нарушители", reply_markup=markup)
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains="Отключить все активные рассылки"), state="*")
async def config_mailings(message: types.Message):
    """Управление рассылками, включенние/отключение"""
    await db.off_all_tasks()
    await message.answer(text="Все активные рассылки отключены")


async def build_prize_keyboard():
    """Построениклавиатуры с призами"""
    prizes = await db.get_all_type_prizes()

    markup = InlineKeyboardMarkup()

    for prize in prizes:
        markup.row(
            InlineKeyboardButton(text=f"{prize['title']}", callback_data=f"{prize['id']}"),
            InlineKeyboardButton(text=f"{'Отключить' if prize['status'] == True else 'Включить'}",
                                 callback_data=f"{prize['id']}-status-{'FALSE' if prize['status'] == True else 'TRUE'}"),
            InlineKeyboardButton(text="Удалить", callback_data=f"{prize['id']}-delete_prize")
        )
    markup.row(
        InlineKeyboardButton(text="Добавить приз", callback_data="add_new_prize")
    )
    return markup


@dp.message_handler(Text(contains="Редактировать призы"), state=ConfigAdmins.config_main)
async def config_prizes(message: types.Message, state: FSMContext):
    """Редактирование призов"""
    markup = await build_prize_keyboard()
    await message.delete()

    text = "Призы для подарков"
    msg = await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)

    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        data['id_msg_list'] = [msg.message_id]


@dp.callback_query_handler(text=["add_new_prize"], state=ConfigAdmins.config_main)
async def add_new_prize(call: types.CallbackQuery, state: FSMContext):
    """Ловлю нажатие на кнопку Добавить новый приз"""
    await ConfigAdmins.config_admins_prizes_title.set()
    text = "Введите название приза"
    msg = await call.message.answer(text=text)

    async with state.proxy() as data:
        data['msg_id_prize_title'] = msg.message_id


@dp.message_handler(content_types=["text"], state=ConfigAdmins.config_admins_prizes_title)
async def add_new_prize_title(message: types.Message, state: FSMContext):
    """Ловлю ввод от пользователя название приза"""
    await ConfigAdmins.config_main.set()
    title = message.text.strip()
    await message.delete()
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg_id_prize_title'])

    await db.add_new_prize_type(title=title)
    markup = await build_prize_keyboard()

    text = "Призы для подарков"
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=int(data['message_id']), text=text,
                                reply_markup=markup)


@dp.callback_query_handler(text_contains=["delete_prize"], state=ConfigAdmins.config_main)
async def delete_prize(call: types.CallbackQuery, state: FSMContext):
    """Удалить приз"""
    id_prize = call.data.split('-')[0]
    data = await state.get_data()
    await db.del_prize_from_db(id=id_prize)

    markup = await build_prize_keyboard()
    text = "Призы для подарков"
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=int(data['message_id']), text=text,
                                reply_markup=markup)


@dp.callback_query_handler(text_contains=["status"], state=ConfigAdmins.config_main)
async def on_off_prize(call: types.CallbackQuery, state: FSMContext):
    """Включение/Отключение приза"""
    data = call.data.split('-')
    id_prize = data[0]
    status = True if data[2] == 'TRUE' else False

    await db.update_status_prize(id_prize=id_prize, status=status)

    data = await state.get_data()

    markup = await build_prize_keyboard()
    text = "Призы для подарков"
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=int(data['message_id']), text=text,
                                reply_markup=markup)
