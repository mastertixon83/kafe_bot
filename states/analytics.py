from aiogram.dispatcher.filters.state import StatesGroup, State


class Analytics(StatesGroup):
    main = State()
    hall_reservation__statistic = State()
    loyal_program_participants_statistic = State()
    hall_reservation_statistic_data = State()
    hall_reservation_statistic_table = State()
