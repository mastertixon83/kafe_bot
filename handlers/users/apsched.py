import datetime
from datetime import timedelta

from aiogram import Bot

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import config
from data.config import admins
from loader import db, scheduler, logger
from utils.db_api.db_commands import DBCommands
import time
import os

db = DBCommands()


async def clear_temp_folder():
    """Очистка папок temp и media/mailings"""
    folders = ["temp", "media/mailings"]
    for folder_name in folders:
        try:
            if folder_name == "media/mailings":
                acive_tasks = await db.get_all_active_tasks()
                file_list = []
                for task in acive_tasks:
                    file_list.append(f"{task['type_mailing']}_{task['picture']}.jpg")
                for filename in os.listdir(folder_name):
                    file_path = os.path.join(folder_name, filename)
                    if os.path.isfile(file_path):
                        if filename not in file_list:
                            os.remove(file_path)

            else:
                for filename in os.listdir(folder_name):
                    file_path = os.path.join(folder_name, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as _ex:
            logger.debug(_ex)


async def send_birthday_cron(bot):
    """Рассылка именинникам"""

    before_birthday_days = config.BEFORE_BIRTHDAY_DAYS
    delta_u = timedelta(days=int(before_birthday_days))

    current_data = datetime.datetime.now().date()
    target_data = current_data + delta_u

    task_info = await db.get_task_birthday()
    await db.update_for_birthday_task_error(task_id=task_info[0]['id'])

    if task_info:
        users = await db.get_birthday_users(target_data=target_data)
        if users:
            picture = task_info[0]['picture']
            text = task_info[0]['message']
            keyboard = task_info[0]['keyboard']

            try:
                for user in users:
                    if not user['administrator']:
                        if keyboard != "None":
                            markup = InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(
                                        text="Забронировать столик" if keyboard == "hall_reservation" else "Заказать доставку",
                                        callback_data="hall_reservation_mailings" if keyboard == "hall_reservation" else "order_shipping_mailings")]
                                ]
                            )
                        else:
                            markup = ""
                        await bot.send_photo(chat_id=user['user_id'], photo=picture, caption=text, reply_markup=markup)
                        time.sleep(2)

            except Exception as _ex:
                logger.error(_ex)
    else:
        for admin in admins:
            await bot.send_message(chat_id=admin,
                                   text="‼️‼️‼️‼️‼️\n Не создана рассылка для именинников! Не забуюте создать")


async def send_message_date(bot, **kwargs):
    """Отправка рассылки на дату"""
    task_id = kwargs.get('task_id')
    users = kwargs.get('users')
    type_mailing = kwargs.get('type_mailing')
    keyboard = kwargs.get('keyboard')
    task_info = await db.get_task_info(task_id=int(task_id))
    picture = task_info[0]['picture']
    text = task_info[0]['message']
    err = "No errors"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="text",
                                  callback_data="cb_data")]
        ]
    )
    markup['inline_keyboard'][0][0]['text'] = "Заказать доставку" if keyboard == 'shipping' else "Забронировать столик"

    for user in users:
        if not user['administrator']:
            try:
                if type_mailing in ["birthday", "hall_reservation"]:
                    markup['inline_keyboard'][0][0]['callback_data'] = "hall_reservation_mailings"
                    await bot.send_photo(chat_id=user['user_id'], photo=picture, caption=text, reply_markup=markup)

                elif type_mailing == "shipping":

                    markup['inline_keyboard'][0][0]['callback_data'] = "order_shipping_mailings"
                    await bot.send_photo(chat_id=user['user_id'], photo=picture, caption=text, reply_markup=markup)

                else:
                    if keyboard != 'None':
                        markup['inline_keyboard'][0][0][
                            'callback_data'] = "order_shipping_mailings" if keyboard == "shipping" else "hall_reservation_mailings"
                    else:
                        markup = ""

                    await bot.send_photo(chat_id=int(user['user_id']), photo=picture, caption=text, reply_markup=markup)

                    time.sleep(2)
                err = 'No Errors'
            except Exception as _ex:
                status = 'Error'
                err = _ex
                logger.error(_ex)
    if type_mailing != 'birthday':
        status = 'performed'
    else:
        status = 'waiting'

    await db.update_task(status=status, error=err, task_id=int(task_id))


"""
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# сохранение задач в json файл
scheduler_state = scheduler.get_state()
with open('scheduler.json', 'w') as f:
    json.dump(scheduler_state, f)
    
# загрузка задач из json файла
with open('scheduler.json', 'r') as f:
    scheduler_state = json.load(f)
scheduler.set_state(scheduler_state)
"""
