from aiogram.utils.callback_data import CallbackData

from utils.db_api.db_commands import DBCommands
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_cd_show = CallbackData("show_menu", "category_id", "message_id")

db = DBCommands()


def make_callback_data(category_id, message_id):
    return menu_cd_show.new(category_id=category_id, message_id=message_id)


async def show_menu_buttons(message_id):
    categories = await db.get_all_categories()

    markup = InlineKeyboardMarkup()

    for category in categories:
        callback_data = make_callback_data(category_id=category['id'], message_id=message_id)
        markup.add(
            InlineKeyboardButton(text=category['title'], callback_data=callback_data)
        )

    return markup