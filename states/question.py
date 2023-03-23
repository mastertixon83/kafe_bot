from aiogram.dispatcher.filters.state import StatesGroup, State


class Question(StatesGroup):
    ask_questions = State()