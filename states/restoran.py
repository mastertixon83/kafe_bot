from aiogram.dispatcher.filters.state import StatesGroup, State


class TableReservation(StatesGroup):
    data = State()
    time = State()
    count_men = State()
    phone = State()
    comment = State()
    check = State()


class TableReservationAdmin(StatesGroup):
    data = State()
