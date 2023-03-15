from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError
from aiogram import types

from loader import db


class DBCommands:
    pool: Connection = db
    ###  Добавление нового пользователя с рефералом и без ###
    ADD_NEW_USER_REFERRAL = "INSERT INTO users(user_id, username, full_name, referral) " \
                            "VALUES ($1, $2, $3, $4) RETURNING id"
    ADD_NEW_USER = "INSERT INTO users(user_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    GET_ALL_USERS = "SELECT * FROM users WHERE ban_status=FALSE"

    ### Удаление пользователя в черный список
    UPDATE_BLACKLIST_STATUS = "UPDATE users SET ban_status = $3, reason_for_ban = $2 WHERE id = $1"
    GET_USER_ID = "SELECT id FROM users WHERE username = $1"

    ### Программа лояльности оформление карты и выбор подтвержденных пользователей $$$
    GET_USER_INFO = "SELECT * FROM users WHERE user_id = $1"
    GET_BLACK_LIST = "SELECT * FROM users WHERE ban_status = TRUE"
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

    ### Заявка на доставку
    ### Добавление новой заявки
    ADD_NEW_SHIPPING_ORDER = "INSERT INTO shipping (tpc, number_of_devices, address, phone, " \
                             "data_reservation, time_reservation, final_summa, pay_method, user_id, user_name)" \
                             "VALUES ($1::jsonb, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id"
    ### Корзина
    ADD_CART = "INSERT INTO cart (item_id, item_count, user_id, title, price) VALUES ($1, $2, $3, $4, $5) RETURNING id"
    UPDATE_CART = "UPDATE cart SET item_count = $1, title = $4, price = $5 WHERE item_id = $2 AND user_id = $3 RETURNING id"
    DELETE_CART = "DELETE FROM cart WHERE user_id = $1"
    CART_INFO = "SELECT * FROM cart WHERE user_id = $1 ORDER BY title"
    GET_CART_PRODUCTS_INFO = "SELECT * FROM items_menu WHERE id = any($1::int[]) ORDER BY id"

    ### Обновление заявки администратором
    UPDATE_SHIPPING_ORDER_STATUS = "UPDATE shipping SET order_status = false, admin_name = $2, admin_id = $3, admin_answer = $4 WHERE id = $1"

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

    ### Настройки Администраторы
    GET_ALL_ADMINS = "SELECT * FROM users WHERE administrator = true"
    REMOVE_ADMIN_STATUS_FROM_USER = "UPDATE users SET administrator = FALSE WHERE id = $1"
    ADD_ADMIN_STATUS_FOR_USER = "UPDATE users SET administrator = TRUE WHERE username = $1"

    ### Рассылки
    ADD_NEW_TASK = "INSERT INTO task(admin_name, type_mailing, picture, message, status, execution_date, error) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id"
    UPDATE_TASK = "UPDATE task SET status=$1, error=$2 WHERE id=$3 RETURNING id"
    GET_TASK_INFO = "SELECT * FROM task WHERE id=$1"
    GET_BIRTHDAY_USERS = "SELECT * FROM users WHERE birthday = $1 and ban_status = FALSE"

    ###  Пользователи
    async def add_new_user(self, referral=None):
        """Добавление нового пользователя с рефералом или без"""
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

    async def update_blacklist_status(self, id, reason, status):
        """Добавление пользователя в черный список"""
        command = self.UPDATE_BLACKLIST_STATUS
        await self.pool.fetch(command, id, reason, status)

    async def get_user_id(self, username):
        """Вывод id пользователя по его username"""
        command = self.GET_USER_ID
        return await self.pool.fetch(command, username)

    ### Программа лояльности
    async def get_user_info(self, user_id):
        """Вывод информации по пользователю"""
        command = self.GET_USER_INFO
        info = await self.pool.fetch(command, str(user_id))
        return info

    async def get_black_list(self):
        """Вывод пользователей, которые в черном списке"""
        command = self.GET_BLACK_LIST
        black_list = await self.pool.fetch(command)
        return black_list

    async def get_all_invited_users(self, referral):
        """Вывод всех пользователе, которые рефералы"""
        command = self.GET_ALL_INVITED
        users = await self.pool.fetch(command, referral)
        return users

    async def update_user_data_card(self, user_id, card_fio, phone_number, birthday):
        """Обновление данных в скидочной карте пользователя"""
        command = self.UPDATE_USER_DATA_CARD
        await self.pool.fetch(command, str(user_id), card_fio, phone_number, birthday)

    async def approve_user_card_admin(self, user_id):
        """Подтверждение карты лояльности админом"""
        command = self.APPROVE_USER_CARD_ADMIN
        await self.pool.fetch(command, str(user_id))

    async def generate_prize_code(self, user_id):
        """Генерация призового кода"""
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
        """Выбор призовых кодов пользователя"""
        command = self.GET_CODE_PRIZE
        code_info = await self.pool.fetch(command, id)
        return code_info

    async def get_code_prize_info(self, code_id):
        """Вывод призового кода пользователя"""
        command = self.GET_CODE_PRIZE_INFO
        code_info = await self.pool.fetch(command, code_id)
        return code_info

    async def update_count_prize(self, user_id, prize_count):
        """Обновление количества полученных подарков"""
        command = self.UPDATE_COUNT_PRIZE
        await self.pool.fetch(command, prize_count, str(user_id))

    async def get_active_codes_user(self, user_id):
        """Вывод активных призовых кодов"""
        command = self.GET_ACTIVE_CODES_USER
        codes = []
        codes = await self.pool.fetch(command, str(user_id))
        return codes

    async def update_prize_code_status(self, code_number):
        """Обновление статуса призового кода (использование)"""
        command = self.UPDATE_PRIZE_CODE_STATUS
        await self.pool.fetch(command, code_number)

    ### Бронирование столика
    async def add_new_order_hall(self, admin_id, order_status, chat_id, user_id, username, full_name, data_reservation,
                                 time_reservation, number_person, phone, comment):
        """Добавление новой заявки на бронирование столика"""

        args = admin_id, order_status, chat_id, user_id, username, full_name, data_reservation, time_reservation, number_person, phone, comment
        command = self.ADD_NEW_ORDER_HALL
        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def get_order_hall_data(self, id):
        """Вывод данных заявки на бронирование столика"""
        command = self.GET_ORDER_HALL_DATA
        data = await self.pool.fetch(command, id)
        return data

    async def get_approved_orders_on_data(self, dataReservation):
        """Вывод подтвержденных заявок на бронирование столика на указанную дату"""
        command = self.GET_APPROVED_ORDERS_ON_DATA
        data = await self.pool.fetch(command, dataReservation)
        return data

    async def update_order_hall_status(self, id, order_status, admin_answer, updated_at, admin_id, admin_name,
                                       table_number):
        """Обновление статуса заявки на бронирование столика"""
        command = self.UPDATE_ORDER_HALL_STATUS
        await self.pool.fetch(command, int(id), order_status, admin_answer, updated_at, str(admin_id), admin_name,
                              table_number)

    ### Доставка
    async def add_new_shipping_order(self, tpc, number_of_devices, address, phone,
                                     data_reservation, time_reservation, final_summa, pay_method, user_id, user_name):
        """Добавление новой заявки на доставку"""
        command = self.ADD_NEW_SHIPPING_ORDER
        args = tpc, number_of_devices, address, phone, data_reservation, time_reservation, final_summa, pay_method, \
               user_id, user_name

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def update_shipping_order_status(self, id, admin_name, admin_id, admin_answer):
        """Обновление статуса заявки на доставку"""
        command = self.UPDATE_SHIPPING_ORDER_STATUS
        args = id, admin_name, admin_id, admin_answer
        await self.pool.fetch(command, *args)

    ### Административная часть
    async def get_all_categories(self):
        """Выборка всех категорий меню"""
        command = self.GET_ALL_CATEGORIES
        categories = await self.pool.fetch(command)
        return categories

    async def get_category_info(self, id):
        """Выборка информации по конкретной категории"""
        command = self.GET_CATEGORY_INFO
        info = await self.pool.fetch(command, id)
        return info

    async def get_item_info(self, id):
        """Выборка информации по конкретному блюду"""
        command = self.GET_ITEM_INFO
        info = await self.pool.fetch(command, id)
        return info

    async def get_all_items_in_category(self, category_id):
        """Выборка всех блюд в категории"""
        command = self.GET_ALL_ITEMS_IN_CATEGORY
        items = await self.pool.fetch(command, category_id)
        return items

    async def update_category(self, title, id, url):
        """Изменение названия категории меню"""
        command = self.UPDATE_CATEGORY
        await self.pool.fetch(command, title, id, url)

    async def update_category_position(self, id, position):
        """изменение позиции категории меню"""
        command = self.UPDATE_CATEGORY_POSITION
        await self.pool.fetch(command, id, position)

    async def add_new_category(self, title, url):
        """Добавление новой категории в тменю"""
        command = self.ADD_NEW_CATEGORY
        try:
            record_id = await self.pool.fetchval(command, title, url)
            return record_id
        except UniqueViolationError:
            pass

    async def delete_category(self, id):
        """Удаление категории из меню"""
        command = self.DELETE_CATEGORY
        await self.pool.fetch(command, id)

    async def add_new_dish(self, title, description, price, photo, category_id):
        """Добавление нового блюда в меню"""
        command = self.ADD_NEW_DISH
        try:
            record_id = await self.pool.fetchval(command, title, description, float(price), photo, int(category_id))
            return record_id
        except UniqueViolationError:
            pass

    async def update_dish(self, title, description, price, photo, item_id):
        """Изменение данных по блюду"""
        command = self.UPDATE_DISH
        args = title, description, float(price), photo, int(item_id)
        await self.pool.fetch(command, *args)

    async def delete_item(self, id):
        """Удаление блюда из меню"""
        command = self.DELETE_ITEM
        await self.pool.fetch(command, id)

    ### Корзина
    async def add_new_cart(self, item_id, item_count, user_id, title, price):
        """Создание новой корзины пользователя"""
        command = self.ADD_CART
        args = item_id, item_count, user_id, title, price
        cart_id = await self.pool.fetchval(command, *args)
        return cart_id

    async def update_cart(self, item_id, item_count, user_id, title, price):
        """Обновление корзины пользователя"""
        command = self.UPDATE_CART
        args = item_count, item_id, user_id, title, price
        cart_id = await self.pool.fetch(command, *args)
        return cart_id

    async def delete_cart(self, user_id):
        """Удаление корзины пользователя"""
        command = self.DELETE_CART
        await self.pool.fetch(command, user_id)

    async def cart_info(self, user_id):
        """Вывод информации по корзине пользователя"""
        command = self.CART_INFO
        return await self.pool.fetch(command, user_id)

    async def get_cart_products_info(self, id_list):
        """Вывод информации о товарах в корзине пользоваителя"""
        command = self.GET_CART_PRODUCTS_INFO
        return await self.pool.fetch(command, id_list)

    ### Настройки
    async def get_all_admins(self):
        """Вывод всех пользователей со статусом администратора"""
        command = self.GET_ALL_ADMINS
        admins = await self.pool.fetch(command)
        return admins

    async def remove_admin_status_from_user(self, id):
        """Удаление статуса администратора у пользователя"""
        command = self.REMOVE_ADMIN_STATUS_FROM_USER
        return await self.pool.fetch(command, id)

    async def add_admin_status_for_user(self, username):
        """Добавление статуса администратора пользователю"""
        command = self.ADD_ADMIN_STATUS_FOR_USER
        return await self.pool.fetch(command, username)

    ### Рассылки
    async def add_new_task(self, admin_name, type_mailing, picture, message, status, execution_date, error):
        """Добавление нового задания в очередь"""
        command = self.ADD_NEW_TASK
        args = admin_name, type_mailing, picture, message, status, execution_date, error
        task_id = await self.pool.fetchval(command, *args)
        return task_id

    async def update_task(self, status, error, task_id):
        """Обновление задания"""
        command = self.UPDATE_TASK
        args = status, error, task_id
        task_id = await self.pool.fetch(command, *args)
        return task_id

    async def get_task_info(self, task_id):
        """Выборка задания по id"""
        command = self.GET_TASK_INFO
        task_info = await self.pool.fetch(command, task_id)
        return task_info

    async def get_all_users(self):
        command = self.GET_ALL_USERS
        return await self.pool.fetch(command)

    async def get_birthday_users(self, target_data):
        command = self.GET_BIRTHDAY_USERS
        return await self.pool.fetch(command, target_data)
