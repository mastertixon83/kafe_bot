from loader import dp, bot

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.personal import StaffCall


@dp.message_handler(Text(equals=["Официант", "Кальянный мастер"]), state=None)
async def waiter(message: Message, state: FSMContext):
    if message.text == 'Официант':
        text = 'Введите номер столика и комментарий для официанта, если Вам что-нибудь нужно.\n\n' \
        '(Например: стол 1, принесите счет)'
        await StaffCall.waiter.set()
    elif message.text == 'Кальянный мастер':
        text = 'Введите номер столика и комментарий для кальянного мастера, если Вам что-нибудь нужно.\n\n' \
               '(Например: стол 1, раскурите кальян)'
        await StaffCall.hookah_master.set()
    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=["text"], state=StaffCall)
async def reg_loyal_card_fio(message: types.Message, state: FSMContext):
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