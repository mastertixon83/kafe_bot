from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailings(StatesGroup):
    main = State()
    standard_mailing_picture = State()
    standard_mailing_text = State()
    standard_sending_method = State()
    standard_sending_data = State()
    standard_sending_button = State()