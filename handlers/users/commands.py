import string

from loader import dp
from aiogram import types

import os, json


@dp.message_handler(commands=['send_article'])
async def send_article(message: types.Message):
    await dp.bot.send_message(message.from_user.id,'Спасибо ваша статья отправлена на модерацию')

# @dp.message_handler()
# async def mat_filter(message: types.Message):
    # """Фильтр матов"""
    # if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}.intersection(
    #     set(json.load(open('cenz.json')))
    # ) != set():
    #     await message.reply('Маты запрещены')
    #     await message.delete()
