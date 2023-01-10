import time
from aiogram.dispatcher import FSMContext

from keyboards.default import menuUser, menuAdmin
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from data.config import admins
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError

from loader import dp, bot, db
from aiogram.types import ReplyKeyboardRemove
from utils.db_api.db_commands import DBCommands

db=DBCommands()


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):

    if message.from_user.username == None:
        text = "Мы рады преветствовать Тебя в нашем чат-боте.\n" \
               "В Товем профиле не указано имя пользователя.\n" \
               "Для правильной работы бота это необходимо сделать. \n\n " \
               "Войди в настройки профиля и введи имя пользователя, после этого нажми /start в боте"

        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        return
    current_state = await state.get_state()
    if current_state is None:
        pass
    else:
        await state.finish()

    text = "👋👋👋Мы рады приветствовать тебя в нашем чат-боте! \
            По этому хотим подарить тебе пиццу 4 сыра абсолютно БЕСПЛАТНО при первом посещении !\n\n"
    text +="Важно! Заполни карту лояльности находясь в заведении в присутствии официанта и пицца твоя! 😉\n\n"
    text +="Еще одна прекрасная новость для тебя! За каждые 5 рекомендаций нас через бота своим друзьям и знакомым "
    text += "ты получишь кальян в ПОДАРОК 🎁"

    id = message.from_user.id

    if id in admins:
        await message.answer(text, reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text, reply_markup=menuUser)

    if message.get_args():
        id_user = await db.add_new_user(referral=message.get_args())
    else:
        id_user = await db.add_new_user()


