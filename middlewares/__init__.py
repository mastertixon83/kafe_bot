from aiogram import Dispatcher

# from .throttling import ThrottlingMiddleware
from .black_list import BlacklistMiddleware


def setup(dp: Dispatcher):
    # dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(BlacklistMiddleware())
