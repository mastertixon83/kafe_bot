from aiogram.dispatcher.filters.state import StatesGroup, State


class CardLoyalReg(StatesGroup):
    fio = State()
    birthday = State()
    phone = State()
    approve = State()


class UsePrizeCode(StatesGroup):
    use_prize = State()