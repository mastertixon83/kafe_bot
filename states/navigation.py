from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()
    edit_category_title = State()
    edit_item_title = State()
    edit_item_desc = State()
    edit_item_price = State()
    edit_item_photo = State()