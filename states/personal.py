from aiogram.dispatcher.filters.state import StatesGroup, State


# Вызов персонала
class StaffCall(StatesGroup):
    waiter = State()
    hookah_master = State()
