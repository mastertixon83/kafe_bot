from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    """Класс состояний для управления редактированием меню"""
    main = State()
    loyal_program = State()
    what_to_edit = State()
    category_title = State()
    category_url = State()
    edit_category_position = State()
    item_title = State()
    item_desc = State()
    item_price = State()
    item_photo = State()


class ConfigAdmins(StatesGroup):
    """Класс состояний для управления администраторами"""
    config_main = State()
    config_admins_list = State()
    config_admins_name = State()
    config_admins_prizes_title = State()


class ConfigBlackList(StatesGroup):
    """Класс состояний для управления черным списком"""
    config_blacklist = State()
    config_blacklist_username = State()
    config_blacklist_ban_reason = State()
    config_blacklist_unban = State()
