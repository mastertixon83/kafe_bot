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
@dp.message_handler(Text(equals=["Официант", "Кальянный мастер"]), state=None)
async def waiter(message: Message, state: FSMContext):
    await message.delete()
    if message.text == 'Официант':

        user_id = message.from_user.id
        codes = await db.get_active_codes_user(user_id)

        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке

        for code in codes:
            markup.add(InlineKeyboardButton(f"{str(code['code'])} - {code['code_description']}",
                                            callback_data=f"prize_code-{str(code['code'])}"))

        text = 'Введите номер столика и комментарий для официанта, если Вам что-нибудь нужно.\n\n' \
        '(Например: стол 1, принесите счет)'
        await StaffCall.waiter.set()
    elif message.text == 'Кальянный мастер':
        text = 'Введите номер столика и комментарий для кальянного мастера, если Вам что-нибудь нужно.\n\n' \
               '(Например: стол 1, раскурите кальян)'
        await StaffCall.hookah_master.set()

    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)
    await message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(content_types=["text"], state=StaffCall)
async def waiter_go(message: types.Message, state: FSMContext):
    await message.delete()
    cur_state = await state.get_state()
    if cur_state == 'StaffCall:waiter':
        text = "Официант уже на пути к Вам"
        personal = 'Официанта'
    elif cur_state == 'StaffCall:hookah_master':
        text = "Кальянный мастер уже на пути к Вам"
        personal = 'Кальянного мастера'

    await message.answer(text, reply_markup=menuUser, parse_mode=types.ParseMode.HTML)
    await state.finish()

    table_comment = message.text.split(',')
    text = f'{table_comment[0]} (@{message.from_user.username}) вызвал {personal} \n\n' \
            f'Комментарий: {table_comment[1]}'
    await bot.send_message(chat_id=admins[0], text=text)