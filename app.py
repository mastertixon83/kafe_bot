import asyncio
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
    # scheduler.shutdown()


async def on_startup(dp):
    await set_default_commands(dp)
    await create_db()
    await on_startup_notify(dp)

    scheduler.start()
    notification_time = config.BIRTHDAY_NOTIFICATION_TIME.split(":")

    # scheduler.add_job(apsched.planer_main, trigger='interval', minutes=3, id='main', kwargs={'bot': dp.bot})
    job = scheduler.add_job(apsched.send_birthday_cron, trigger='cron', day="*", hour=notification_time[0],
                       minute=notification_time[1], args=(dp.bot,))
    # print(job.next_run_time)

    # scheduler.add_job(apsched.send_message_cron, trigger='cron', hour=15, minute=15, args=(dp.bot,))


if __name__ == '__main__':

    dp.middleware.setup(middlewares.BlacklistMiddleware())

    if not os.path.isdir("media"):
        os.mkdir("media")

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
