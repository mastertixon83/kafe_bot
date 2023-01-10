from aiogram import types
from data.config import admins
from loader import dp


# @dp.message_handler()
# async def bot_echo(message: types.Message):
#     text = f'Отправитель @{message.from_user.username}\n Статья\n{message.text}'
#     await dp.bot.send_message(admins[0], text=text)
#     await message.delete()
#     await message.answer('Спасибо! Ваша статья отправлена на модерацию')