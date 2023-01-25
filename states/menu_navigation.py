from aiogram.dispatcher.filters.state import StatesGroup, State


class MenuNavigation(StatesGroup):
    categories = State()
    items = State()