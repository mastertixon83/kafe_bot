from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError
from aiogram import types

from loader import bot, dp, db


class DBCommands:
    pool: Connection = db
    ###  Добавление нового пользователя с рефералом и без ###
    ADD_NEW_USER_REFERRAL = "INSERT INTO users(user_id, username, full_name, referral) " \
                            "VALUES ($1, $2, $3, $4) RETURNING id"
    ADD_NEW_USER = "INSERT INTO users(user_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"

    ### Программа лояльности оформление карты и выбор подтвержденных пользователей $$$
    GET_USER_INFO = "SELECT * FROM users WHERE user_id = $1"
    GET_ALL_INVITED = "SELECT * FROM users WHERE referral = $1"
    UPDATE_USER_DATA_CARD = "UPDATE users SET card_fio = $2, card_phone = $3, birthday = $4 " \
                            " WHERE user_id = $1"
    APPROVE_USER_CARD_ADMIN = "UPDATE users SET card_status = TRUE WHERE user_id = $1"
    GENERATE_PRIZE_CODE = "INSERT INTO codes(user_id, code_description) VALUES ($1, $2) RETURNING id"
    UPDATE_COUNT_PRIZE = "UPDATE users SET prize = $1 WHERE user_id = $2"
    GET_CODE_PRIZE = "SELECT * FROM codes WHERE id = $1"
    GET_ACTIVE_CODES_USER = "SELECT * FROM codes WHERE user_id = $1 and code_status = TRUE"

    ### Добавление заявки на бронирование столика
    ADD_NEW_ORDER = "INSERT INTO orders(admin_id, order_status, chat_id, user_id, username, full_name, " \
                    "data_reservation, time_reservation, number_person, phone)" \
                    "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING order_id"

    GET_ORDER_DATA = "SELECT * FROM orders WHERE order_id = $1"
    UPDATE_ORDER_STATUS = "UPDATE orders SET order_status = $2, admin_answer = $3, updated_at = $4, admin_id = $5, adminname = $6 WHERE order_id = $1"

    ###  Добавление нового пользователя с рефералом и без ###
    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        chat_id = user.id
        username = user.username
        full_name = user.full_name

        if referral:
            args = chat_id, username, full_name, referral
            command = self.ADD_NEW_USER_REFERRAL
        else:
            args = chat_id, username, full_name
            command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    ### Программа лояльности оформление карты и выбор подтвержденных пользователей $$$
    async def get_user_info(self, user_id):
        command = self.GET_USER_INFO
        info = await self.pool.fetch(command, user_id)
        return info

    async def get_all_invited_users(self, referral):
        command = self.GET_ALL_INVITED
        users = await self.pool.fetch(command, referral)
        return users

    async def update_user_data_card(self, user_id, card_fio, phone_number, birthday):
        command = self.UPDATE_USER_DATA_CARD
        await self.pool.fetch(command, int(user_id), card_fio, phone_number, birthday)

    async def approve_user_card_admin(self, user_id):
        command = self.APPROVE_USER_CARD_ADMIN
        await self.pool.fetch(command, int(user_id))

    async def generate_prize_code(self, user_id):
        user = types.User.get_current()
        chat_id = user.id
        description = "Бесплатное занятие"

        args = chat_id, description
        command = self.GENERATE_PRIZE_CODE
        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def get_code_prize(self, code_id):
        command = self.GET_CODE_PRIZE
        code_info = await self.pool.fetch(command, code_id)
        return code_info

    async def update_count_prize(self, user_id, prize_count):
        command = self.UPDATE_COUNT_PRIZE
        await self.pool.fetch(command, prize_count, user_id)

    async def get_active_codes_user(self, user_id):
        command = self.GET_ACTIVE_CODES_USER
        codes = []
        codes = await self.pool.fetch(command, user_id)
        return codes

    ### Бронирование столика
    async def add_new_order(self, admin_id, order_status, chat_id, user_id, username, full_name, data_reservation,
                            time_reservation, number_person, phone):

        args = admin_id, order_status, chat_id, user_id, username, full_name, data_reservation, time_reservation, number_person, phone
        command = self.ADD_NEW_ORDER
        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def get_order_data(self, order_id):
        command = self.GET_ORDER_DATA
        data = await self.pool.fetch(command, order_id)
        return data

    async def update_order_status(self, order_id, order_status, admin_answer, updated_at, admin_id, adminname):
        command = self.UPDATE_ORDER_STATUS
        await self.pool.fetch(command, int(order_id), order_status, admin_answer, updated_at, int(admin_id), adminname)


