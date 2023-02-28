from aiogram.dispatcher.filters.state import StatesGroup, State


class Shipping(StatesGroup):
    data = State()
    time = State()
    number_of_devices = State()
    address = State()
    phone = State()
    pay_method = State()
    check = State()