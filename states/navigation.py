from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()
    what_to_edit = State()
    edit_category = State()
    new_category = State()
    item_title = State()
    item_desc = State()
    item_price = State()
    item_photo = State()