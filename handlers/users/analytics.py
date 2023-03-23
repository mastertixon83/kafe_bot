# TODO: смотреть заявки на доставку, которые были созданы сегодня
# TODO: статистика по забраным призам
# TODO: Отправит Excel файл
from datetime import datetime, timezone, timedelta
import csv

from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from aiogram import types

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from keyboards.default.menu import menuAdmin, newsletter_kbd, analytics_kbd
from states.analytics import Analytics
from utils.db_api.db_commands import DBCommands

from aiogram.dispatcher.filters import Text
from data.config import admins
import logging

db = DBCommands()

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)


def plural_form(n, word):
    """Определение правильного написания формы слова"""
    if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} {word}а"
    else:
        return f"{n} {word}"


def data_preparation():
    """Подготовка дат для запроса"""
    # За сегодня
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    # За неделю
    today_week = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date_week = today_week - timedelta(days=today_week.weekday() + 4)
    end_date_week = start_date_week + timedelta(days=7)

    # За предыдущий месяц
    today_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date_month = (today_month - timedelta(days=1)).replace(day=1)
    end_date_month = today_month

    # За месяц
    today_prev_month = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date_prev_month = today_prev_month.replace(day=1)
    end_date_prev_month = today_prev_month + timedelta(days=1)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_date_week": start_date_week,
        "end_date_week": end_date_week,
        "start_date_month": start_date_month,
        "end_date_month": end_date_month,
        "start_date_prev_month": start_date_prev_month,
        "end_date_prev_month": end_date_prev_month
    }


@dp.callback_query_handler(text=["excel_users"], state=Analytics.main)
async def download_users_to_excel(call: types.CallbackQuery, state: FSMContext):
    """Выгрузка пользователей в Excel файл"""
    all_users_info = await db.get_all_users()
    curr_dt = datetime.now().strftime("%d_%m_%Y %H:%M")
    result = []
    for user in all_users_info:
        created_at = user["created_at"]
        user_id = user["user_id"]
        username = user["username"]
        full_name = user["full_name"]
        gender = user["gender"]
        employment = user["employment"]
        referral = user["referral"]
        referral_id = user["referral_id"]
        card_fio = user["card_fio"]
        card_phone = user["card_phone"]
        card_number = user["card_number"]
        card_status = user["card_status"]
        birthday = user["birthday"]
        prize = user["prize"]
        balance = user["balance"]
        administrator = "Администратор" if user["administrator"] == True else None
        director = "Директор" if user["director"] == True else None
        ban_status = "Забанен" if user["ban_status"] == True else None
        reason_for_ban = user["reason_for_ban"]

        result.append(
            [created_at, user_id, username, full_name, gender, employment, referral, referral_id, card_fio,
             card_phone, card_number, card_status, birthday, prize, balance, administrator, director, ban_status,
             reason_for_ban]
        )

    with open(f"result_{curr_dt}.csv", "a") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Дата регистрации",
                "User_id",
                "Username",
                "Full_name",
                "Пол",
                "Вид занятости",
                "Referral",
                "Referral_id",
                "Фамилия Имя на карте",
                "Номер телефона",
                "Номер карты",
                "Статус карты",
                "День рождения",
                "Призовые коды",
                "Использовано призовых кодов",
                "Администратор",
                "Директор",
                "Статус бана",
                "Причина бана",
            )
        )

        writer.writerows(result)


@dp.message_handler(Text(contains=["Пользователи"]), state=Analytics.main)
async def analytics_users(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Пользователи"""
    await message.delete()
    users_nb_info = await db.get_all_nb_users()
    all_users_info = await db.get_all_users()

    text = f"Активных пользователей: {len(users_nb_info)}\nВсего пользователей: {len(all_users_info)}"
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="Выгрузить Excel файл", callback_data="excel_users")
    )
    msg = await message.answer(text=text, reply_markup=markup)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains=["Рассылки"]), state=Analytics.main)
async def analytics_mailings(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Формы рассылок-анкет"""
    await message.delete()
    total = 0
    type_mailing_list = ["standard", "birthday", "hall_reservation", "shipping", "loyal_card"]
    type_mailing_dict = {
        "standard": "📨 Обычная рассылка",
        "birthday": "🎁 Предложение для именинников",
        "hall_reservation": "🍽 Призыв к бронированию",
        "shipping": "🚚 Закажите доставку",
        "loyal_card": "💳 Владельцам карт лояльности"}
    text = ""
    kwargs = data_preparation()
    for item in type_mailing_list:
        # За сегодня
        today_count = len(
            await db.get_tasks_mailing(type_mailing=item, start_date=kwargs['start_date'], end_date=kwargs['end_date']))
        # За неделю
        week_count = len(
            await db.get_tasks_mailing(type_mailing=item, start_date=kwargs['start_date_week'], end_date=kwargs['end_date_week']))
        # За предыдущий месяц
        month_count = len(
            await db.get_tasks_mailing(type_mailing=item, start_date=kwargs['start_date_month'], end_date=kwargs['end_date_month']))
        # За месяц
        prev_month_count = len(
            await db.get_tasks_mailing(type_mailing=item,
                                       start_date=kwargs['start_date_prev_month'].replace(day=1) - timedelta(days=1),
                                       end_date=kwargs['end_date_prev_month']))

        text += f"<b>{type_mailing_dict[item]}</b>\n"
        text += f" За сегодня: {today_count}\n"
        text += f" За неделю: {week_count}\n"
        text += f" За текущий месяц: {prev_month_count}\n"
        text += f" За предыдущий месяц: {month_count}\n"
        text += "-" * 80 + "\n"

    msg = await message.answer(text=text)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains=["Статистика вызовова персонала"]), state=Analytics.main)
async def analytics_personal(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Статистика вызовов персоналов"""
    await message.delete()
    # За сегодня
    kwargs = data_preparation()
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    who1 = "Официанта"
    who2 = "Кальянного мастера"
    today_count1 = len(await db.get_personal_request_today(personal=who1, start_date=kwargs['start_date'], end_date=kwargs['end_date']))
    today_count2 = len(await db.get_personal_request_today(personal=who2, start_date=kwargs['start_date'], end_date=kwargs['end_date']))

    text = "<b>За сегодня вызывали персонал</b>\n"
    text += f"{who1}: {plural_form(today_count1, 'раз')}\n"
    text += f"{who2}: {plural_form(today_count2, 'раз')}"

    msg = await message.answer(text=text)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains=["Статистика бронирований"]), state=Analytics.main)
async def analytics_hall_reservation(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Статистика бронирований"""
    await message.delete()
    # За сегодня
    kwargs = data_preparation()
    today_count = len(await db.get_approved_orders_hall(start_date=kwargs['start_date'], end_date=kwargs['end_date']))

    # За неделю
    week_count = len(await db.get_approved_orders_hall(start_date=kwargs['start_date_week'], end_date=kwargs['end_date_week']))

    # За предыдущий месяц
    month_count = len(await db.get_approved_orders_hall(start_date=kwargs['start_date_month'], end_date=kwargs['end_date_month']))

    # За месяц
    prev_month_count = len(
        await db.get_approved_orders_hall(start_date=kwargs['start_date_prev_month'].replace(day=1) - timedelta(days=1),
                                          end_date=kwargs['end_date_prev_month']))

    total = len(await db.get_all_approved_orders_hall())

    text = "<b>Бронирования (подтвержденные)</b>\n"
    text += f"За сегодня: {today_count}\n"
    text += f"За неделю: {week_count}\n"
    text += f"За текущий месяц: {prev_month_count}\n"
    text += f"За предыдущий месяц: {month_count}\n"
    text += "-" * 80
    text += f"Всего: {total}\n"

    msg = await message.answer(text=text)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains=["Статистика доставки"]), state=Analytics.main)
async def analytics_shipping(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Статистика доставки"""
    await message.delete()
    kwargs = data_preparation()
    # За сегодня
    today_count = len(await db.get_approved_shipping(start_date=kwargs['start_date'], end_date=kwargs['end_date']))

    # За неделю
    week_count = len(await db.get_approved_shipping(start_date=kwargs['start_date_week'], end_date=kwargs['end_date_week']))

    # За предыдущий месяц
    month_count = len(await db.get_approved_shipping(start_date=kwargs['start_date_month'], end_date=kwargs['end_date_month']))

    # За месяц
    prev_month_count = len(
        await db.get_approved_shipping(start_date=kwargs['start_date_prev_month'].replace(day=1) - timedelta(days=1),
                                       end_date=kwargs['end_date_prev_month']))

    total = len(await db.get_all_approved_shipping())

    text = "<b>Заказы на доставку (подтвержденные)</b>\n"
    text += f"За сегодня: {today_count}\n"
    text += f"За неделю: {week_count}\n"
    text += f"За текущий месяц: {prev_month_count}\n"
    text += f"За предыдущий месяц: {month_count}\n"
    text += "-" * 80
    text += f"Всего: {total}\n"

    msg = await message.answer(text=text)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)
    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.message_handler(Text(contains=["Участники программы лояльности"]), state=Analytics.main)
async def analytics_loyal_program_participants(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Участники программы лояльности"""
    await message.delete()
    loyal_program_participants_info = await db.get_loyal_program_participants()
    markup = InlineKeyboardMarkup()
    for user_info in loyal_program_participants_info:
        markup.add(
            InlineKeyboardButton(text=user_info["username"],
                                 callback_data=f"{user_info['user_id']}-user_info")
        )
    msg = await message.answer(text="Участники программы лояльности", reply_markup=markup)

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
        data["markup"] = markup


@dp.callback_query_handler(text_contains=["user_info"], state=Analytics.main)
async def show_user_info(call: types.CallbackQuery, state: FSMContext):
    """Показать информацию о пользователе"""
    callback_data = call.data.split('-')
    data = await state.get_data()
    user_info = await db.get_user_info(user_id=callback_data[0])
    all_invited_users = await db.get_all_invited_users(user_info[0]["referral_id"])

    count_users = len(all_invited_users)
    created_at = user_info[0]['created_at']

    text = f"Информаци о пользователе @{user_info[0]['username']}\n\n"
    text += f"Дата регистрации: {datetime.strftime(created_at, '%Y-%m-%d')}\n"
    text += f"Фамилия и Имя: {user_info[0]['card_fio']}\n"
    text += f"Номер карты: {user_info[0]['card_number']}\n"
    text += f"Дата рождения: {user_info[0]['birthday']}\n"
    text += f"Пришло к нам по рекомендации: {plural_form(count_users, 'человек')}\n"
    text += f"Номер телефона: {user_info[0]['card_phone']}\n"

    msg = await call.message.edit_text(text=text)
    await call.message.edit_reply_markup(data["markup"])

    data = await state.get_data()
    id_msg_list = data['id_msg_list']
    id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list
