from aiogram.dispatcher.filters.state import StatesGroup, State


class Shipping(StatesGroup):
    title_item = State()
    portion_quantity = State()
    number_of_devices = State()
    data = State()
    time = State()
    address = State()
    phone = State()
    pay_method = State()
    check = State()