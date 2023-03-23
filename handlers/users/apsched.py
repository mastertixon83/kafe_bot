import datetime
from datetime import timedelta

from aiogram import Bot

from data import config
from data.config import admins
from loader import db, scheduler
from utils.db_api.db_commands import DBCommands
import time

db = DBCommands()


async def send_birthday_cron(bot, **kwargs):
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
            caption = task_info[0]['message']

            try:
                for user in users:
                    if user['administrator'] != True:
                        await bot.send_photo(chat_id=user['user_id'], photo=picture, caption=caption)
                        time.sleep(2)

            except Exception as _ex:
                pass
    else:
        await bot.send_message(chat_id=admins[0], text="‼️‼️‼️‼️‼️\n Не создана рассылка для именинников! Не забуюте создать")


async def send_message_date(bot, **kwargs):
    """Отправка рассылки на дату"""
    task_id = kwargs.get('task_id')
    users = kwargs.get('users')
    type_mailing = kwargs.get('type_mailing')
    task_info = await db.get_task_info(task_id=int(task_id))
    picture = task_info[0]['picture']
    caption = task_info[0]['message']
    try:
        for user in users:
            if user['administrator'] != True:
                await bot.send_photo(chat_id=int(user['user_id']), photo=picture, caption=caption)
                time.sleep(2)
            # await bot.send_photo(chat_id=user['user_id'], photo=picture, caption=caption)
        # await bot.send_message(chat_id=553603641, text='date')
        if type_mailing != 'birthday':
            status = 'performed'
        else:
            status = 'waiting'
        error = 'No Errors'
    except Exception as _ex:
        status = 'Error'
        error = _ex
    await db.update_task(status=status, error=error, task_id=int(task_id))


async def send_message_cron(bot, **kwargs):
    await bot.send_message(chat_id=553603641, text='Cron')


async def send_message_interval(bot, **kwargs):
    caption = kwargs.get('caption')
    picture = kwargs.get('picture')

    await bot.send_photo(chat_id=553603641, caption=caption, photo=picture)
