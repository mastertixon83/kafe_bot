#TODO: варианты на кнопках
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
        await db.update_last_activity(user_id=message.from_user.id, button='Вызов официанта')
        user_id = message.from_user.id
        codes = await db.get_active_codes_user(user_id)

        text = 'Введите номер столика и комментарий для официанта, если Вам что-нибудь нужно.\n\n' \
               '(Например: стол 1, принесите счет)'
        await StaffCall.waiter.set()

    elif message.text == '👲 Кальянный мастер':
        await db.update_last_activity(user_id=message.from_user.id, button='Вызов кальянного мастера')
        text = 'Введите номер столика и комментарий для кальянного мастера, если Вам что-нибудь нужно.\n\n' \
               '(Например: стол 1, раскурите кальян)'
        await StaffCall.hookah_master.set()

    await message.answer(text=text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=["text"], state=StaffCall)
async def waiter_go(message: types.Message, state: FSMContext):
    """Ловлю комментарий от пользователя"""
    await db.update_last_activity(user_id=message.from_user.id, button='Вызов персонала комментарий')
    cur_state = await state.get_state()

    separator = ""
    if "." in message.text:
        separator = '.'
    elif "," in message.text:
        separator = ","
    elif " " in message.text:
        separator = " "
    else:
        await message.answer(text="Введите комментарий корректно. (Например: стол 1, принесите счет)")
        return

    if cur_state == 'StaffCall:waiter':
        text = "Официант уже на пути к Вам"
        personal = 'Официанта'
    elif cur_state == 'StaffCall:hookah_master':
        text = "Кальянный мастер уже на пути к Вам"
        personal = 'Кальянного мастера'

    if str(message.chat.id) in admins:
        markup = menuAdmin
    else:
        markup = menuUser

    await message.answer(text, reply_markup=markup, parse_mode=types.ParseMode.HTML)
    await state.finish()

    table_comment = message.text.split(separator)

    text = f'{table_comment[0]} (@{message.from_user.username}) вызвал {personal} \n\n' \
           f'Комментарий: {table_comment[1]}'

    for admin in admins:
        await bot.send_message(chat_id=admin, text=text)

    await db.add_personal_request(who=personal, table_number=table_comment[0], comment=table_comment[1])
