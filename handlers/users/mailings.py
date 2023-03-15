import os
from datetime import datetime, timezone, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.users import apsched

from loader import dp, bot, db, scheduler
from aiogram import types

from keyboards.default.menu import cancel_btn, newsletter_kbd
from aiogram.dispatcher import FSMContext
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text

from states.mailings import Mailings

db = DBCommands()


@dp.message_handler(Text(contains="Обычная рассылка"), state=Mailings.main)
async def standard_mailing(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Обычная рассылка"""
    await Mailings.standard_mailing_picture.set()

    data = await state.get_data()

    text = "Загрузите изображение для рассылки"
    msg = await message.answer(text=text, reply_markup=cancel_btn)

    id_msg_list = []
    try:
        id_msg_list = data['id_msg_list']
    except Exception as _ex:
        pass

    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['admin_name'] = message.from_user.username


@dp.message_handler(lambda message: not message.photo, state=Mailings.standard_mailing_picture)
async def check_standard_mailing_photo(message: types.Message, state: FSMContext):
    """Проверка на тип сообщения, картинка или нет"""
    await message.delete()

    data = await state.get_data()

    text = "Это не изображение!\n\n"
    text += "Загрузите изображение для рассылки"

    return await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Mailings.standard_mailing_picture)
async def standard_mailing_picture(message: types.Message, state: FSMContext):
    """Ловлю изображение для стандартной рассылки"""
    await Mailings.standard_mailing_text.set()

    try:
        await message.photo[-1].download(f'media/mailings/standard_{message.photo[-1].file_id}.jpg')
    except Exception as _ex:
        os.mkdir("media/mailings")
        await message.photo[-1].download(f'media/mailings/standard_{message.photo[-1].file_id}.jpg')

    data = await state.get_data()

    text = "Введите сообщение рассылки"
    msg = await message.answer(text=text, reply_markup=cancel_btn)

    id_msg_list = []
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['standard_mailing_picture'] = message.photo[-1].file_id


@dp.message_handler(content_types=["text"], state=Mailings.standard_mailing_text)
async def standard_mailing_text(message: types.Message, state: FSMContext):
    """Ловлю текст стандартной рассылки"""
    await Mailings.standard_sending_method.set()

    message_text = message.text.strip()
    data = await state.get_data()

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="📅 Указать дату", callback_data="delayed_mailing"),
        InlineKeyboardButton(text="📤 Отправить немедленно", callback_data="send_immediately"),
    )
    msg = await message.answer(text="Выберите способ отпарвки", reply_markup=markup)

    id_msg_list = []
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data['message_text'] = message_text


@dp.callback_query_handler(text=["delayed_mailing", "send_immediately"], state=Mailings.standard_sending_method)
async def standard_mailing_sending_method(call: types.CallbackQuery, state: FSMContext):
    """Ловлю от пользователя способ отправки"""
    await call.answer()

    data = await state.get_data()
    admin_name = data["admin_name"]
    type_mailing = "standard"
    picture = data["standard_mailing_picture"]
    message_text = data["message_text"]
    id_msg_list = data["id_msg_list"]

    if call.data == "send_immediately":
        date = datetime.now()
        minute_later = date + timedelta(minutes=1)

        task_id = await db.add_new_task(admin_name=admin_name, type_mailing=type_mailing, picture=picture,
                                        message=message_text, status="waiting", execution_date=minute_later,
                                        error="No error")
        try:
            scheduler.add_job(apsched.send_message_date, 'date', run_date=minute_later, id='job_1',
                              kwargs={'bot': bot, 'task_id': task_id})
            text = f"Рассылка запланирована на {minute_later.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as _ex:
            text = f"Рассылка не запланирована - Ошибка: {_ex}"
            await db.update_task(task_id=int(task_id), status="error", error=_ex)

        await call.message.delete()
        # performed
        # waiting
        # draft
        # error
        msg = await call.message.answer(text=text)
        id_msg_list.append(msg.message_id)

        await state.finish()
        await Mailings.main.set()

        async with state.proxy() as data:
            data["id_msg_list"] = id_msg_list
            data["task_id"] = task_id

    elif call.data == "delayed_mailing":
        await Mailings.standard_sending_data.set()
        await call.message.delete()
        text = f"Укажите время и дату рассылки в формате ГГГГ-ММ-ДД ЧЧ:ММ \n\nСегодня {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        await call.message.answer(text=text)


@dp.message_handler(content_types=["text"], state=Mailings.standard_sending_data)
async def standard_mailing_date_time(message: types.Message, state: FSMContext):
    """Ловлю дату и время рассылки"""
    date = message.text.strip() + ":00"

    data = await state.get_data()

    admin_name = data["admin_name"]
    type_mailing = "standard"
    picture = data["standard_mailing_picture"]
    message_text = data["message_text"]
    id_msg_list = data["id_msg_list"]

    try:

        task_id = await db.add_new_task(admin_name=admin_name, type_mailing=type_mailing, picture=picture,
                                        message=message_text, status="waiting", execution_date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
                                        error="No error")
        try:
            scheduler.add_job(apsched.send_message_date, 'date', run_date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S"), id='job_1',
                              kwargs={'bot': bot, 'task_id': task_id})
            text = f"Рассылка запланирована на {datetime.strptime(date, '%Y-%m-%d %H:%M:%S')}"
        except Exception as _ex:
            text = f"Рассылка не запланирована - Ошибка: {_ex}"
            await db.update_task(task_id=int(task_id), status="error", error=_ex)

        msg = await message.answer(text=text)

        id_msg_list.append(msg.message_id)

        await state.finish()
        await Mailings.main.set()

        async with state.proxy() as data:
            data["id_msg_list"] = id_msg_list

    except Exception as _ex:
        print(_ex)
        await message.answer(text="Я Вас не понимаю. Введите корректные данные в формате ГГГГ-ММ-ДД ЧЧ:ММ")
