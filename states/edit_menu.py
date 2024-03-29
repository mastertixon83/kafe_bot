from aiogram.dispatcher.filters.state import StatesGroup, State


# Редактирование категории
class EditCategory(StatesGroup):
    list_categories = State()
    edit_category = State()


# Редактирование блюда
class EditItem(StatesGroup):
    edit_item_select_category = State()
    edit_item_title = State()
    edit_item_desc = State()
    edit_item_photo = State()
    edit_item_price = State()
