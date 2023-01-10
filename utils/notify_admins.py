import logging
from aiogram import Dispatcher
from data.config import admins
from keyboards.default import menuAdmin


async def on_startup_notify(dp: Dispatcher):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, "Бот Запущен", reply_markup=menuAdmin)

        except Exception as err:
            logging.exception(err)


async def on_shutdown_notify(dp: Dispatcher):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, "Бот остановлен")
            await dp.bot.close()
        except Exception as err:
            logging.exception(err)