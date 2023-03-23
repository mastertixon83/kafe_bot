from aiogram.dispatcher.filters.state import StatesGroup, State


class Review(StatesGroup):
    send_review = State()
