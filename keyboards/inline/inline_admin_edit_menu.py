from aiogram.utils.callback_data import CallbackData
from utils.db_api.db_commands import DBCommands
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_cd = CallbackData("show_menu", "level", "category_id", "item_id", "what")

db = DBCommands()


def make_callback_data(level, category_id=0, item_id=0, what="0"):
    return menu_cd.new(level=level, category_id=category_id, item_id=item_id, what=what)


async def what_to_edit_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup()

    what_dict = {"Категории": "category", "Блюда": "items"}

    for key, value in what_dict.items():
        button_text = f"{key}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, what=value)

        markup.add(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    return markup


async def categories_keyboard():
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()

    categories = await db.get_all_categories()

    for category in categories:
        button_text = f"{category['title']}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category_id=category['id'])

        markup.add(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    return markup


async def items_in_category_keyboard(category_id):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()
    items = await db.get_all_items_in_category(int(category_id))

    if len(items) == 0:
        return

    for item in items:
        button_text = f"{item['title']}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, item_id=item['id'])

        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    markup.add(
        InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1)),
        InlineKeyboardButton(text="Добавить", callback_data=make_callback_data(what="new_item"))
    )

    return markup
