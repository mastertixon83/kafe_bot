from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from utils.db_api.db_commands import DBCommands

db = DBCommands()


# Middleware для проверки пользователя на черный список
class BlacklistMiddleware(BaseMiddleware):

    async def on_pre_process_update(self, update: types.Update, data: dict):
        b_list = []
        for item in await db.get_black_list():
            b_list.append(item['user_id'])

        print(b_list)
        if update.message:
            user = update.message.from_user.id
        elif update.callback_query:
            user = update.callback_query.from_user.id
        else: return

        if str(user) in b_list:
            await update.message.answer("Вы в черном списке", reply_markup=ReplyKeyboardRemove())
            print("You BANED")
            raise CancelHandler()

    async def on_process_update(self, update: types.Update, data: dict):
        print('process update')

