from aiogram.dispatcher.filters.state import StatesGroup, State


class Shipping(StatesGroup):
    main = State()
    data = State()
    time = State()
    number_of_devices = State()
    address = State()
    phone = State()
    pay_method = State()
    check = State()


class Cart(StatesGroup):
    cart = State()