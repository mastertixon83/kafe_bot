import asyncio

from aiogram import executor
from data import config

from utils.notify_admins import on_startup_notify, on_shutdown_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.sql import create_db

# https://www.youtube.com/watch?v=ke7LP4LDXSg
# https://www.youtube.com/watch?v=rQ-6SdpdYys
async def on_shutdown(dp):
    await on_shutdown_notify(dp)


async def on_startup(dp):
    await set_default_commands(dp)
    await create_db()
    await on_startup_notify(dp)

if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
