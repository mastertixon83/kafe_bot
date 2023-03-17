from loader import dp, bot

from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.personal import StaffCall
from utils.db_api.db_commands import DBCommands

db = DBCommands()
@dp.message_handler(Text(["👦 Официант", "👲 Кальянный мастер"]), state="*")
async def waiter(message: Message, state: FSMContext):
    """Ловлю выбор персонала от пользователя"""

    if message.text == '👦 Официант':

        user_id = message.from_user.id
        codes = await db.get_active_codes_user(user_id)

        text = 'Введи номер столика и комментарий для официанта, если Тебе что-нибудь нужно.\n\n' \
        '(Например: стол 1, принесите счет)'
        await StaffCall.waiter.set()

    elif message.text == '👲 Кальянный мастер':
        text = 'Введи номер столика и комментарий для кальянного мастера, если Тебе что-нибудь нужно.\n\n' \
               '(Например: стол 1, раскурите кальян)'
        await StaffCall.hookah_master.set()

    await message.answer(text=text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=["text"], state=StaffCall)
async def waiter_go(message: types.Message, state: FSMContext):
    """Ловлю комментарий от пользователя"""
    cur_state = await state.get_state()
    if cur_state == 'StaffCall:waiter':
        text = "Официант уже на пути к Тебе"
        personal = 'Официанта'
    elif cur_state == 'StaffCall:hookah_master':
        text = "Кальянный мастер уже на пути к Тебе"
        personal = 'Кальянного мастера'

    await message.answer(text, reply_markup=menuUser, parse_mode=types.ParseMode.HTML)
    await state.finish()

    separator = ""
    if "." in message.text:
        separator = '.'
    elif "," in message.text:
        separator = ","
    elif " " in message.text:
        separator = " "
    table_comment = message.text.split(separator)
    text = f'{table_comment[0]} (@{message.from_user.username}) вызвал {personal} \n\n' \
            f'Комментарий: {table_comment[1]}'
    await bot.send_message(chat_id=admins[0], text=text)