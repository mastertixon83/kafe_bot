from aiogram.dispatcher.filters.state import StatesGroup, State


# Редактирование категории
class Dating(StatesGroup):
    user_gender = State()
    user_age = State()