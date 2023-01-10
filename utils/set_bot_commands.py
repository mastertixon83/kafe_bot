from aiogram import types

async def set_default_commands(dp):
    """Установка комманд по умолчанияю"""
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить бота'),
            types.BotCommand('help', 'Вывести справку'),
            types.BotCommand('send_article', 'Отправить статью на модерацию'),
            types.BotCommand('parser', 'Запустить парсер', ),

        ]
    )
