from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailings(StatesGroup):
    main = State()
    standard_mailing_picture = State()
    standard_mailing_text = State()
    standard_sending_method = State()
    standard_sending_data = State()
    questionnaire = State()
    call_reservation_picture = State()
    call_reservation_text = State()
    call_reservation_data = State()
    loyalty_cardholders_picture = State()
    loyalty_cardholders_text = State()
    loyalty_cardholders_data = State()
    group_users_picture = State()
    group_users_text = State()
    group_users_data = State()
    user_picture = State()
    user_text = State()
    user_data = State()