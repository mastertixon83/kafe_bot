from aiogram import Dispatcher

from .black_list import BlacklistMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(BlacklistMiddleware())
