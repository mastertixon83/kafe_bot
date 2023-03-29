#TODO: Настроить админов
import asyncio
import datetime
import os

from aiogram import executor
import middlewares, filters, handlers
from handlers import dp
from data import config
from handlers.users import apsched

from loader import scheduler, logger

from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.sql import create_db
from utils.db_api.db_commands import DBCommands

db = DBCommands()


# https://www.youtube.com/watch?v=ke7LP4LDXSg
# https://www.youtube.com/watch?v=rQ-6SdpdYys
async def on_shutdown(dp):
    await on_shutdown_notify(dp)
    scheduler.shutdown()


async def on_startup(dp):
    await set_default_commands(dp)
    await create_db()

    administrators = await db.get_all_admins()
    main_admin = config.admins[0]
    config.admins.clear()
    config.admins.append(main_admin)
    for admin in administrators:
        config.admins.append(admin['user_id'])

    await on_startup_notify(dp)
    scheduler.start()
    # BOT_TOKEN=6040617089:AAFbKfUPqPnW1_UkikhefvayTlrGQoBq6G4
    # BOT_TOKEN=5664820788:AAEfWKPVB8myVcLkpdNKpurc1mY5yogUzuc
    notification_time = config.BIRTHDAY_NOTIFICATION_TIME.split(":")
    #TODO: сделать задание каждое утро очищать папку temp и media/mailings
    scheduler.add_job(apsched.send_birthday_cron, 'cron', hour=str(notification_time[0]),
                      minute=str(notification_time[1]), kwargs={'bot': dp.bot})

    scheduler.add_job(apsched.clear_temp_folder, 'cron', hour="00", minute="00", kwargs={'bot': dp.bot})


if __name__ == '__main__':
    try:
        dp.middleware.setup(middlewares.BlacklistMiddleware())

        if not os.path.isdir("media"):
            os.mkdir("media")

        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception as _ex:
        logger.error(_ex)
