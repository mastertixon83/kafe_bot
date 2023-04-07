import datetime

from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError
from aiogram import types

from loader import db


class DBCommands:
    pool: Connection = db

    ### Отзывы
    ADD_NEW_REVIEW = "INSERT INTO review(text, username)  VALUES ($1, $2) RETURNING id"
    GET_APPROVED_REVIEWS = "SELECT * FROM review WHERE status = TRUE ORDER BY updated_at DESC"
    UPDATE_STATUS_REVIEW = "UPDATE review SET status = TRUE WHERE id = $1"
    DEACTIVATE_REVIEW = "UPDATE review SET status = FALSE WHERE id = $1"

    ###  Добавление нового пользователя с рефералом и без ###
    ADD_NEW_USER_REFERRAL = "INSERT INTO users(user_id, username, full_name, referral, gender, age_group) " \
                            "VALUES ($1, $2, $3, $4, $5, $6) RETURNING id"
    ADD_NEW_USER = "INSERT INTO users(user_id, username, full_name, gender, age_group) VALUES ($1, $2, $3, $4, $5) RETURNING id"
    GET_ALL_NB_USERS = "SELECT user_id, administrator FROM users WHERE ban_status=FALSE"
    GET_ALL_USERS = "SELECT * FROM users ORDER BY id"
    UPDATE_LAST_ACTIVITY = "UPDATE users SET last_activity = $2 WHERE user_id = $1"
    GET_USER_BY_USERNAME = "SELECT * FROM users WHERE username = $1"

    ### Добавление пользователя в черный список
    UPDATE_BLACKLIST_STATUS = "UPDATE users SET ban_status = $3, reason_for_ban = $2, ban_date = $4 WHERE id = $1"
    GET_USER_ID = "SELECT id FROM users WHERE username = $1"

    ### Программа лояльности оформление карты и выбор подтвержденных пользователей $$$
    GET_USER_INFO = "SELECT * FROM users WHERE user_id = $1"
    GET_BLACK_LIST = "SELECT * FROM users WHERE ban_status = TRUE"

    GET_ALL_INVITED = "SELECT * FROM users WHERE referral = $1"  # приглашенные друзья

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
    UPDATE_ORDER_HALL_STATUS = "UPDATE orders_hall SET order_status = $2, admin_answer = $3, admin_id = $4, admin_name = $5, table_number = $6 WHERE id = $1"
    # GET_APPROVED_ORDERS_ON_DATA = "SELECT data_reservation, time_reservation, table_number FROM orders_hall WHERE data_reservation = $1 AND (order_status=true AND admin_answer = 'approved') ORDER BY table_number"
    GET_APPROVED_ORDERS_ON_DATA = "SELECT * FROM orders_hall WHERE (data_reservation = $1 AND order_status=false AND admin_answer = 'approve') ORDER BY table_number"

    ### Заявка на доставку
    ADD_NEW_SHIPPING_ORDER = "INSERT INTO shipping (tpc, number_of_devices, address, phone, " \
                             "data_reservation, time_reservation, final_summa, pay_method, user_id, user_name)" \
                             "VALUES ($1::jsonb, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING id"
    ### Корзина
    ADD_CART = "INSERT INTO cart (item_id, item_count, user_id, title, price) VALUES ($1, $2, $3, $4, $5) RETURNING id"
    UPDATE_CART = "UPDATE cart SET item_count = $1, title = $4, price = $5 WHERE item_id = $2 AND user_id = $3 RETURNING id"
    DELETE_ITEM_FROM_CART = "DELETE FROM cart WHERE item_id = $1"
    GET_USER_CART = "SELECT * FROM cart WHERE user_id = $1"
    GET_USER_CART_ITEM_INFO = "SELECT * FROM cart WHERE user_id = $1 and item_id = $2"
    DELETE_CART = "DELETE FROM cart WHERE user_id = $1"
    CART_INFO = "SELECT * FROM cart WHERE user_id = $1 ORDER BY title"
    GET_CART_PRODUCTS_INFO = "SELECT * FROM items_menu WHERE id = any($1::int[]) ORDER BY id"

    ### Обновление заявки на доставку администратором
    UPDATE_SHIPPING_ORDER_STATUS = "UPDATE shipping SET order_status = $5, admin_name = $2, admin_id = $3, admin_answer = $4 WHERE id = $1"

    ### Персонал
    ADD_PERSONAL_REQUEST = "INSERT INTO personal (personal, table_number, comment) VALUES ($1, $2, $3) RETURNING id"

    ### Настройки
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
    REMOVE_ADMIN_STATUS_FROM_USER = "UPDATE users SET administrator = FALSE WHERE user_id = $1"
    ADD_ADMIN_STATUS_FOR_USER = "UPDATE users SET administrator = TRUE WHERE username = $1 RETURNING user_id"

    ### Рассылки
    ADD_NEW_TASK = "INSERT INTO task(admin_name, type_mailing, picture, message, status, execution_date, error, keyboard) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id"
    UPDATE_BEFORE_ADDING = "UPDATE task set status = 'off' WHERE type_mailing = $1 and status = 'waiting'"
    UPDATE_TASK = "UPDATE task SET status=$1, error=$2 WHERE id=$3 RETURNING id"
    GET_TASK_INFO = "SELECT * FROM task WHERE id=$1"
    GET_TASK_BIRTHDAY = "SELECT * FROM task WHERE type_mailing = 'birthday' and status = 'waiting'"
    GET_BIRTHDAY_USERS = "SELECT * FROM users WHERE EXTRACT(DAY FROM birthday) = $1 AND EXTRACT(MONTH FROM birthday) = $2;"
    GET_LOYAL_PROGRAM_PARTICIPANTS = "SELECT * FROM users WHERE card_status = TRUE"
    UPDATE_FOR_BIRTHDAY_TASK_ERROR = "UPDATE task SET error = 'No errors' WHERE id = $1"
    GET_ALL_UNCOMPLETED_TASKS = "SELECT * FROM task WHERE status = 'waiting' and execution_date < $1"

    ### Настройки рассылок
    OFF_ALL_TASK = "UPDATE task set status = 'off' WHERE status = 'waiting'"

    ### Настройки Призы
    GET_ALL_TYPE_PRIZES = "SELECT * FROM prize ORDER BY title"
    ADD_NEW_PRIZE_TYPE = "INSERT INTO prize(title) VALUES($1)"
    DEL_PRIZE_FROM_DB = "DELETE FROM prize WHERE id = $1"
    UPDATE_STATUS_PRIZE = "UPDATE prize SET status = $1 WHERE id = $2"
    GET_ACTIVE_PRIZE = "SELECT * FROM prize WHERE status = TRUE"

    ### Аналитика
    GET_APPROVED_ORDERS_HALL = "SELECT * FROM orders_hall WHERE admin_answer = 'approve' and updated_at >= $1 AND updated_at < $2"
    GET_ALL_APPROVED_ORDERS_HALL = "SELECT * FROM orders_hall WHERE admin_answer = 'approve'"
    GET_ALL_ORDER_HALL_MADE_TODAY = "SELECT * FROM orders_hall WHERE created_at = $1"
    GET_ORDERS_HALL_ON_DATE = "SELECT * FROM orders_hall WHERE data_reservation = $1 ORDER BY time_reservation"

    GET_APPROVED_SHIPPING = "SELECT * FROM shipping WHERE admin_answer = 'approve' and updated_at >= $1 AND updated_at < $2"
    GET_ALL_APPROVED_SHIPPING = "SELECT * FROM shipping WHERE admin_answer = 'approve'"
    GET_SHIPPING_ORDER_MADE_TODAY = "SELECT * FROM shipping WHERE created_at = $1"

    GET_PERSONAL_REQUEST_TODAY = "SELECT * FROM personal WHERE personal = $1 and created_at >= $2 AND created_at < $3"

    GET_TASKS_MAILING = "SELECT * FROM task WHERE type_mailing = $1 and updated_at >= $2 AND updated_at < $3"
    GET_ALL_ACTIVE_TASKS = "SELECT * FROM task WHERE status = 'waiting'"
    OFF_TASK = "UPDATE task SET status = 'off' WHERE id = $1"

    ### Отзывы
    async def add_new_review(self, text, username):
        """Добавление нового отзыва"""
        command = self.ADD_NEW_REVIEW
        args = text, username
        return await self.pool.fetch(command, *args)

    async def get_approved_reviews(self):
        """Выбор одобренных отзывов"""
        command = self.GET_APPROVED_REVIEWS
        return await self.pool.fetch(command)

    async def update_status_review(self, id):
        """Одобрение отзыва"""
        command = self.UPDATE_STATUS_REVIEW
        await self.pool.fetch(command, int(id))

    async def deactivate_review(self, id):
        """Отключение отзыва"""
        command = self.DEACTIVATE_REVIEW
        await self.pool.fetch(command, int(id))

    ###  Пользователи
    async def add_new_user(self, referral=None, gender="", age_group=""):
        """Добавление нового пользователя с рефералом или без"""
        user = types.User.get_current()
        chat_id = str(user.id)
        username = user.username
        full_name = user.full_name

        if referral:
            args = chat_id, username, full_name, referral, gender, age_group
            command = self.ADD_NEW_USER_REFERRAL
        else:
            args = chat_id, username, full_name, gender, age_group
            command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def update_blacklist_status(self, id, reason, status, ban_date):
        """Добавление пользователя в черный список"""
        command = self.UPDATE_BLACKLIST_STATUS
        await self.pool.fetch(command, id, reason, status, ban_date)

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

    async def generate_prize_code(self, user_id, description):
        """Генерация призового кода"""
        user = types.User.get_current()

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

    async def update_order_hall_status(self, id, order_status, admin_answer, admin_id, admin_name,
                                       table_number):
        """Обновление статуса заявки на бронирование столика"""
        command = self.UPDATE_ORDER_HALL_STATUS
        await self.pool.fetch(command, int(id), order_status, admin_answer, str(admin_id), admin_name,
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

    async def update_shipping_order_status(self, id, admin_name, admin_id, admin_answer, order_status):
        """Обновление статуса заявки на доставку"""
        command = self.UPDATE_SHIPPING_ORDER_STATUS
        args = id, admin_name, admin_id, admin_answer, order_status
        await self.pool.fetch(command, *args)

    ### Вызов персонала
    async def add_personal_request(self, who, table_number, comment):
        """Вызов персонала, новая заявка"""
        command = self.ADD_PERSONAL_REQUEST
        args = who, table_number, comment
        return await self.pool.fetch(command, *args)

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
        info = await self.pool.fetch(command, int(id))
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

    async def delete_item_From_cart(self, item_id):
        """Удаление блюда из корзины при счетчике = 0"""
        command = self.DELETE_ITEM_FROM_CART
        await self.pool.fetch(command, item_id)

    async def get_user_cart(self, user_id):
        """Показать корзину"""
        command = self.GET_USER_CART
        cart = await self.pool.fetch(command, str(user_id))
        return cart

    async def get_user_cart_item_info(self, user_id, item_id):
        """Выбор информации пользовательской корзины по элементу заказа"""
        command = self.GET_USER_CART_ITEM_INFO
        args = str(user_id), int(item_id)
        item_cart_info = await self.pool.fetch(command, *args)
        return item_cart_info

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

    async def off_all_tasks(self):
        """Отключение всех активных рассылок"""
        command = self.OFF_ALL_TASK
        await self.pool.fetch(command)

    ### Рассылки
    async def add_new_task(self, admin_name, type_mailing, picture, message, status, execution_date, error, keyboard):
        """Добавление нового задания в очередь"""
        command = self.ADD_NEW_TASK
        args = admin_name, type_mailing, picture, message, status, execution_date, error, keyboard
        task_id = await self.pool.fetchval(command, *args)
        return task_id

    async def update_before_adding(self, type_mailing):
        """Обновление задачи перед добавлением новой"""
        command = self.UPDATE_BEFORE_ADDING
        await self.pool.fetch(command, type_mailing)

    async def update_task(self, status, error, task_id):
        """Обновление задания"""
        command = self.UPDATE_TASK
        args = status, str(error), int(task_id)
        task_id = await self.pool.fetch(command, *args)
        return task_id

    async def get_task_info(self, task_id):
        """Выборка задания по id"""
        command = self.GET_TASK_INFO
        task_info = await self.pool.fetch(command, int(task_id))
        return task_info

    async def get_task_birthday(self):
        """Выбор рассылки для именинников"""
        command = self.GET_TASK_BIRTHDAY
        return await self.pool.fetch(command)

    async def get_all_nb_users(self):
        """Выбор всех пользователей, которые не забанены"""
        command = self.GET_ALL_NB_USERS
        return await self.pool.fetch(command)

    async def get_all_users(self):
        """Выбор всех пользователей"""
        command = self.GET_ALL_USERS
        users = await self.pool.fetch(command)
        return users

    async def get_loyal_program_participants(self):
        """Выбор участников программы лояльности"""
        command = self.GET_LOYAL_PROGRAM_PARTICIPANTS
        return await self.pool.fetch(command)

    async def update_for_birthday_task_error(self, task_id):
        """Обновление времени отправки для рассылки именинников"""
        command = self.UPDATE_FOR_BIRTHDAY_TASK_ERROR
        await self.pool.fetch(command, task_id)

    async def get_all_uncompleted_tasks(self, execution_date):
        """Выбор всех активных рассылок"""
        command = self.GET_ALL_UNCOMPLETED_TASKS
        return await self.pool.fetch(command, execution_date)

    async def update_last_activity(self, user_id, button):
        """Обновоение даты и времени последней активности пользователя"""
        command = self.UPDATE_LAST_ACTIVITY
        args = str(user_id), button
        await self.pool.fetch(command, *args)

    async def get_user_by_username(self, username):
        """Выбрать пользователя по username"""
        command = self.GET_USER_BY_USERNAME
        return await self.pool.fetch(command, username)

    async def get_birthday_users(self, target_data):
        """Выбор именинников"""
        command = self.GET_BIRTHDAY_USERS
        data_obj = target_data
        args = data_obj.day, data_obj.month
        users = await self.pool.fetch(command, *args)
        return users

    async def get_all_type_prizes(self):
        """Выбо всех призов из БД"""
        command = self.GET_ALL_TYPE_PRIZES
        prizes = await self.pool.fetch(command)
        return prizes

    async def add_new_prize_type(self, title):
        """Добавление нового типа приза"""
        command = self.ADD_NEW_PRIZE_TYPE
        await self.pool.fetch(command, title)

    async def del_prize_from_db(self, id):
        """Удаление приза из БД"""
        command = self.DEL_PRIZE_FROM_DB
        await self.pool.fetch(command, int(id))

    async def update_status_prize(self, id_prize, status):
        """Включение/Отключение приза"""
        command = self.UPDATE_STATUS_PRIZE
        args = status, int(id_prize)
        await self.pool.fetch(command, *args)

    async def get_active_prize(self):
        """Выбор активного приза"""
        command = self.GET_ACTIVE_PRIZE
        return await self.pool.fetch(command)

    async def get_approved_orders_hall(self, start_date, end_date):
        """Выбор подтвержденных бронирований за сегодня, неделю, месяц, прошлый месяц"""
        command = self.GET_APPROVED_ORDERS_HALL
        args = start_date, end_date
        orders = await self.pool.fetch(command, *args)
        return orders

    async def get_all_approved_orders_hall(self):
        """Выбор всех бронирований подтвержденных администратором"""
        command = self.GET_ALL_APPROVED_ORDERS_HALL
        return await self.pool.fetch(command)

    async def get_all_order_hall_made_today(self, date):
        """Выбор всех бронирований сделанных сегодня"""
        command = self.GET_ALL_ORDER_HALL_MADE_TODAY
        return await self.pool.fetch(command, date)

    async def get_orders_hall_on_date(self, date):
        """Выбор всех бронирований на дату"""
        command = self.GET_ORDERS_HALL_ON_DATE
        return await self.pool.fetch(command, date)

    async def get_approved_shipping(self, start_date, end_date):
        """Выбор доставок подтвержденных администратором за сегодня, за неделю, за месяц, за предыдущий месяц"""
        command = self.GET_APPROVED_SHIPPING
        args = start_date, end_date
        return await self.pool.fetch(command, *args)

    async def get_all_approved_shipping(self):
        """Выбор всех подтвержденных администратором доставок"""
        command = self.GET_ALL_APPROVED_SHIPPING
        return await self.pool.fetch(command)

    async def get_personal_request_today(self, personal, start_date, end_date):
        """Выбор заявок вызова персонала"""
        command = self.GET_PERSONAL_REQUEST_TODAY
        args = personal, start_date, end_date
        return await self.pool.fetch(command, *args)

    async def get_shipping_order_made_today(self, date):
        """Выбор заявок на доставку сделанных сегодня"""
        command = self.GET_SHIPPING_ORDER_MADE_TODAY
        return await self.pool.fetch(command, date)

    async def get_tasks_mailing(self, type_mailing, start_date, end_date):
        """Выбор подписок для статистики"""
        command = self.GET_TASKS_MAILING
        args = type_mailing, start_date, end_date
        return await self.pool.fetch(command, *args)

    async def get_all_active_tasks(self):
        """Выбор всех активных рассылок"""
        command = self.GET_ALL_ACTIVE_TASKS
        return await self.pool.fetch(command)

    async def off_task(self, task_id):
        """Отключение задания на рассылку"""
        command = self.OFF_TASK
        await self.pool.fetch(command, int(task_id))
