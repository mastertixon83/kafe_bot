from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailings(StatesGroup):
    main = State()
    mailing_picture = State()
    mailing_text = State()
    sending_method = State()
    sending_data = State()
    sending_button = State()