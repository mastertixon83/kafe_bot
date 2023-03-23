from aiogram.utils.callback_data import CallbackData
from utils.db_api.db_commands import DBCommands
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_cd = CallbackData("shipping_oder", "level", "category_id", "item_id", "user_id", "action", "what", "minus", "count", "plus")

db = DBCommands()


def make_callback_data(level, category_id="0", item_id="0", user_id="0",action="None", what="None", minus="-", count="0", plus="+", text="None"):
    return menu_cd.new(level=level, category_id=category_id, item_id=item_id, user_id=user_id, action=action,
                       what=what, minus=minus,
                       count=count, plus=plus)


### Построение клавиатуры с категориями
async def categories_keyboard(user_id):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()

    categories = await db.get_all_categories()
    action = "None"

    for category in categories:
        count = await db.get_all_items_in_category(category_id=int(category['id']))
        if len(count) == 0: continue
        else:

            button_text = f"{category['title']}"
            position_text = f"{category['position']}"

            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, action=action, category_id=category['id'])

            ### построение основных кнопок
            markup.add(
                InlineKeyboardButton(text=button_text, callback_data=callback_data),
            )
    ### Добавление последних кнопок
    markup.row(
        InlineKeyboardButton(text="✅ Оформить доставку", callback_data=make_callback_data(level=3, what="ordering")),
        InlineKeyboardButton(text="Главное меню", callback_data=make_callback_data(level=-1, what="exit"))
    )
    cart = await db.get_user_cart(user_id=user_id)
    sum = 0
    for item in cart:
        sum += item['price'] * item['item_count']

    markup.row(
        InlineKeyboardButton(text=f"🛒 Корзина - Заказ на {sum}", callback_data=make_callback_data(level=999, what="cart"))
    )

    return markup


### Построение клавиатуры с блюдами категории
async def items_in_category_keyboard(item_id, count, user_id="0", text="None"):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()

    callback_data_minus = make_callback_data(level=222, action="del_shipping", user_id=user_id, item_id=item_id, count=count)
    callback_data_count = make_callback_data(level=999, action="add_shipping", count=count)
    callback_data_plus = make_callback_data(level=221, action="add_shipping", user_id=user_id, item_id=item_id, count=count)

    markup.add(
        InlineKeyboardButton(text="-", callback_data=callback_data_minus),
        InlineKeyboardButton(text=str(count), callback_data="count"),
        InlineKeyboardButton(text="+", callback_data=str(callback_data_plus))
    )

    return markup
