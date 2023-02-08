from utils.db_api.db_commands import DBCommands
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


db = DBCommands()


async def show_menu_buttons():
    categories = await db.get_all_categories()

    markup = InlineKeyboardMarkup()

    for category in categories:
        markup.add(
            InlineKeyboardButton(text=category['title'], url=category['url'])
        )

    return markup