from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()
    what_to_edit = State()
    edit_new_category_title = State()
    edit_new_item_title = State()
    edit_new_item_desc = State()
    edit_new_item_price = State()
    edit_new_item_photo = State()