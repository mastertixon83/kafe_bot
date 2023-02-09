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

    GENERATE_PRIZE_CODE = "INSERT INTO prize_codes(user_id, code_description) VALUES ($1, $2) RETURNING id"
    UPDATE_COUNT_PRIZE = "UPDATE users SET prize = $1 WHERE user_id = $2"

    GET_CODE_PRIZE = "SELECT * FROM prize_codes WHERE id = $1"
    GET_CODE_PRIZE_INFO = "SELECT * FROM prize_codes WHERE code = $1"
    GET_ACTIVE_CODES_USER = "SELECT * FROM prize_codes WHERE user_id = $1 and code_status = TRUE"

    UPDATE_PRIZE_CODE_STATUS = "UPDATE prize_codes set code_status = FALSE WHERE code = $1"

    ### Заявки на бронирование столика
    ADD_NEW_ORDER_HALL = "INSERT INTO orders_hall(admin_id, order_status, chat_id, user_id, username, full_name, " \
                         "data_reservation, time_reservation, number_person, phone, comment)" \
                         "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING id"

    GET_ORDER_HALL_DATA = "SELECT * FROM orders_hall WHERE id = $1"
    UPDATE_ORDER_HALL_STATUS = "UPDATE orders_hall SET order_status = $2, admin_answer = $3, updated_at = $4, admin_id = $5, admin_name = $6, table_number = $7 WHERE id = $1"
    # GET_APPROVED_ORDERS_ON_DATA = "SELECT data_reservation, time_reservation, table_number FROM orders_hall WHERE data_reservation = $1 AND (order_status=true AND admin_answer = 'approved') ORDER BY table_number"
    GET_APPROVED_ORDERS_ON_DATA = "SELECT * FROM orders_hall WHERE (data_reservation = $1 AND order_status=true AND admin_answer = 'approved') ORDER BY table_number"

    ### Административная часть
    ### Редактирование меню
    GET_ALL_CATEGORIES = "SELECT * FROM category_menu ORDER BY position"
    GET_ALL_ITEMS_IN_CATEGORY = "SELECT * FROM items_menu WHERE category_id = $1"

    GET_CATEGORY_INFO = "SELECT * FROM category_menu WHERE id = $1"
    GET_ITEM_INFO = "SELECT * FROM items_menu WHERE id = $1"

    ADD_NEW_CATEGORY = "INSERT INTO category_menu(title, url) VALUES ($1, $2) RETURNING id"
    UPDATE_CATEGORY = "UPDATE category_menu SET title = $1, url = $3 WHERE id = $2"
    UPDATE_CATEGORY_POSITION = "UPDATE category_menu SET position=$2 WHERE id = $1"

    ADD_NEW_DISH = "INSERT INTO items_menu(title, description, price, photo, category_id) VALUES ($1, $2, $3, $4, $5) RETURNING id"
    UPDATE_DISH = "UPDATE items_menu SET title=$1, description=$2, price=$3, photo=$4 WHERE id = $5"

    DELETE_CATEGORY = "DELETE FROM category_menu WHERE id = $1"
    DELETE_ITEM = "DELETE FROM items_menu WHERE id = $1"

    ###  Добавление нового пользователя с рефералом и без ###

    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        chat_id = str(user.id)
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
        info = await self.pool.fetch(command, str(user_id))
        return info

    async def get_all_invited_users(self, referral):
        command = self.GET_ALL_INVITED
        users = await self.pool.fetch(command, referral)
        return users

    async def update_user_data_card(self, user_id, card_fio, phone_number, birthday):
        command = self.UPDATE_USER_DATA_CARD
        await self.pool.fetch(command, str(user_id), card_fio, phone_number, birthday)

    async def approve_user_card_admin(self, user_id):
        command = self.APPROVE_USER_CARD_ADMIN
        await self.pool.fetch(command, str(user_id))

    async def generate_prize_code(self, user_id):
        user = types.User.get_current()
        description = "Бесплатная пицца"

        args = str(user_id), description
        command = self.GENERATE_PRIZE_CODE
        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def get_code_prize(self, id):
        command = self.GET_CODE_PRIZE
        code_info = await self.pool.fetch(command, id)
        return code_info

    async def get_code_prize_info(self, code_id):
        command = self.GET_CODE_PRIZE_INFO
        code_info = await self.pool.fetch(command, code_id)
        return code_info

    async def update_count_prize(self, user_id, prize_count):
        command = self.UPDATE_COUNT_PRIZE
        await self.pool.fetch(command, prize_count, str(user_id))

    async def get_active_codes_user(self, user_id):
        command = self.GET_ACTIVE_CODES_USER
        codes = []
        codes = await self.pool.fetch(command, str(user_id))
        return codes

    async def update_prize_code_status(self, code_number):
        command = self.UPDATE_PRIZE_CODE_STATUS
        await self.pool.fetch(command, code_number)

    ### Бронирование столика
    async def add_new_order_hall(self, admin_id, order_status, chat_id, user_id, username, full_name, data_reservation,
                                 time_reservation, number_person, phone, comment):

        args = admin_id, order_status, chat_id, str(user_id), username, full_name, data_reservation, time_reservation, number_person, phone, comment
        command = self.ADD_NEW_ORDER_HALL
        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def get_order_hall_data(self, id):
        command = self.GET_ORDER_HALL_DATA
        data = await self.pool.fetch(command, id)
        return data

    async def get_approved_orders_on_data(self, dataReservation):
        command = self.GET_APPROVED_ORDERS_ON_DATA
        data = await self.pool.fetch(command, dataReservation)
        return data

    async def update_order_hall_status(self, id, order_status, admin_answer, updated_at, admin_id, admin_name,
                                       table_number):
        command = self.UPDATE_ORDER_HALL_STATUS
        await self.pool.fetch(command, int(id), order_status, admin_answer, updated_at, int(admin_id), admin_name,
                              table_number)

    ### Административная часть
    ### Выборка всех категорий
    async def get_all_categories(self):
        command = self.GET_ALL_CATEGORIES
        categories = await self.pool.fetch(command)
        return categories

    ### Выбрать информацию по категории
    async def get_category_info(self, id):
        command = self.GET_CATEGORY_INFO
        info = await self.pool.fetch(command, id)
        return info

    ### Выборка информации по блюду
    async def get_item_info(self, id):
        command = self.GET_ITEM_INFO
        info = await self.pool.fetch(command, id)
        return info

    ### Выборка всех блюд в категории
    async def get_all_items_in_category(self, category_id):
        command = self.GET_ALL_ITEMS_IN_CATEGORY
        items = await self.pool.fetch(command, category_id)
        return items

    ### Изменение названия категории
    async def update_category(self, title, id, url):
        command = self.UPDATE_CATEGORY
        await self.pool.fetch(command, title, id, url)

    ### Изменение позиции категории
    async def update_category_position(self,id, position):
        command = self.UPDATE_CATEGORY_POSITION
        await self.pool.fetch(command,id, position)

    ### Добавление новой категории
    async def add_new_category(self, title, url):
        command = self.ADD_NEW_CATEGORY
        try:
            record_id = await self.pool.fetchval(command, title, url)
            return record_id
        except UniqueViolationError:
            pass

    ### Удаление категории
    async def delete_category(self, id):
        command = self.DELETE_CATEGORY
        await self.pool.fetch(command, id)

    ### Добавление нового блюда
    async def add_new_dish(self, title, description, price, photo, category_id):
        command = self.ADD_NEW_DISH
        try:
            record_id = await self.pool.fetchval(command, title, description, float(price), photo, int(category_id))
            return record_id
        except UniqueViolationError:
            pass

    ### Редактирование блюда
    async def update_dish(self, title, description, price, photo, item_id):
        command = self.UPDATE_DISH
        args = title, description, float(price), photo, int(item_id)
        await self.pool.fetch(command, *args)

    ### Удаление блюда
    async def delete_item(self, id):
        command = self.DELETE_ITEM
        await self.pool.fetch(command, id)
