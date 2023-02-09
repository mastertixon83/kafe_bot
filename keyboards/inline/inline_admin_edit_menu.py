from aiogram.utils.callback_data import CallbackData
from utils.db_api.db_commands import DBCommands
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


menu_cd = CallbackData("edit_menu", "level", "category_id", "item_id", "action", "what")

db = DBCommands()


def make_callback_data(level, category_id=0, item_id=0, action="None", what="None"):
    return menu_cd.new(level=level, category_id=category_id, item_id=item_id, action=action, what=what)


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


async def categories_keyboard(what):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()

    categories = await db.get_all_categories()
    action = "None"
    # cbd = make_callback_data(level=55)
    # markup.add(
    #     InlineKeyboardButton(text="Позиция", callback_data=cbd),
    #     InlineKeyboardButton(text="Название", callback_data=cbd),
    #     InlineKeyboardButton(text="Ссылка", callback_data=cbd)
    # )
    for category in categories:
        button_text = f"{category['title']}"
        position_text = f"{category['position']}"

        if what == "category":
            action = "edit_category"
        elif what == "items":
            action = "edit_items"

        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, action=action, category_id=category['id'])
        cb_data = make_callback_data(level=13, action="delete_category", category_id=category['id'])
        cb_data_position = make_callback_data(level=14, action="edit_position", category_id=category['id'])

        if action == "edit_category":
            markup.add(
                InlineKeyboardButton(text=position_text, callback_data=cb_data_position),
                InlineKeyboardButton(text=button_text, callback_data=callback_data),
                InlineKeyboardButton(text='🔗', url=category['url']),
                InlineKeyboardButton(text="❌", callback_data=cb_data)

            )

        elif action == "edit_items":
            markup.add(
                InlineKeyboardButton(text=button_text, callback_data=callback_data)
            )
    if what == "category":
        markup.row(
            InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1)),
            InlineKeyboardButton(text="Добавить", callback_data=make_callback_data(level=12, action="new_category"))
        )
    elif what == "items":
        markup.row(
            InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, what="items"))
            # InlineKeyboardButton(text="Добавить", callback_data=make_callback_data(level=22, action="new_item"))
        )
    return markup


async def items_in_category_keyboard(category_id):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()
    items = await db.get_all_items_in_category(int(category_id))

    if len(items) == 0:
        markup.row(
            InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, what="items")),
            InlineKeyboardButton(text="Добавить",
                                 callback_data=make_callback_data(level=22, category_id=category_id, action="new_item"))
        )
        return markup

    for item in items:
        button_text = f"{item['title']}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, action="edit_item", item_id=item['id'], category_id=category_id)
        cb_data = make_callback_data(level=23, action="delete_item", category_id=category_id, item_id=item["id"])

        markup.add(
            InlineKeyboardButton(text=button_text, callback_data=callback_data),
            InlineKeyboardButton(text="❌", callback_data=cb_data)
        )

    markup.row(
        InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, what="items")),
        InlineKeyboardButton(text="Добавить", callback_data=make_callback_data(level=22, category_id=category_id, action="new_item"))
    )

    return markup
