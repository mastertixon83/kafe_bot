from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    main = State()
    what_to_edit = State()
    category_title = State()
    category_url = State()
    edit_category_position = State()
    item_title = State()
    item_desc = State()
    item_price = State()
    item_photo = State()


class ConfigAdmins(StatesGroup):
    config_admins_list = State()
    config_admins_name = State()