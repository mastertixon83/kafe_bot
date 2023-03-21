import asyncio
import datetime
import os

from aiogram import executor
import middlewares, filters, handlers
from handlers import dp
from data import config
from handlers.users import apsched

from loader import scheduler

from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.sql import create_db


# https://www.youtube.com/watch?v=ke7LP4LDXSg
# https://www.youtube.com/watch?v=rQ-6SdpdYys
async def on_shutdown(dp):
    await on_shutdown_notify(dp)
    scheduler.shutdown()


async def on_startup(dp):
    await set_default_commands(dp)
    await create_db()
    await on_startup_notify(dp)

    scheduler.start()
    # BOT_TOKEN=6040617089:AAFbKfUPqPnW1_UkikhefvayTlrGQoBq6G4
    # BOT_TOKEN=5664820788:AAEfWKPVB8myVcLkpdNKpurc1mY5yogUzuc
    notification_time = config.BIRTHDAY_NOTIFICATION_TIME.split(":")

    # scheduler.add_job(apsched.planer_main, trigger='interval', minutes=3, id='main', kwargs={'bot': dp.bot})
    # job = scheduler.add_job(apsched.send_birthday_cron, trigger='data', day="*", hour=notification_time[0],
    #                    minute=notification_time[1], args=(dp.bot,))
    # print(job.next_run_time)
    current_data = datetime.datetime.now()
    before_birthday_days = config.BEFORE_BIRTHDAY_DAYS
    delta_u = datetime.timedelta(days=int(before_birthday_days))
    delta_t = datetime.timedelta(days=1)
    run_dt = current_data.year, current_data.month, current_data.day, current_data.hour, current_data.minute+1

    scheduler.add_job(
        apsched.send_birthday_cron, 'date', run_date=datetime.datetime(*run_dt), id="birthday", kwargs={'bot': dp.bot, }
    )


if __name__ == '__main__':

    dp.middleware.setup(middlewares.BlacklistMiddleware())

    if not os.path.isdir("media"):
        os.mkdir("media")

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
