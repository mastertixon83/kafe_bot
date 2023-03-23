from aiogram.dispatcher.filters.state import StatesGroup, State


class Analytics(StatesGroup):
    main = State()
    users_statistic = State()
    mailings_statistic = State()
    personal_statistic = State()
    shipping_statistic = State()
    hall_reservation__statistic = State()
    loyal_program_participants_statistic = State()
