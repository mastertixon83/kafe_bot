#TODO: У администратора просмотр не использованных кодов
#TODO: Удаление карты лояльности

import os
from datetime import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from utils.db_api.db_commands import DBCommands

from keyboards.default.menu import *
from keyboards.inline.inline_buttons import admin_card_approve, user_inline_approve, get_prize_inline

from loader import dp, bot

from states.card_loyality import CardLoyalReg, UsePrizeCode

from data.config import admins

db = DBCommands()


# Генерация карты лояльности
def card_generate(user_id, user_fio, card_number):
    # 1080*680
    photo = Image.open("template_card.jpg")

    # make the image editable
    drawing = ImageDraw.Draw(photo)

    black = (3, 8, 12)
    pos = (235, 470)
    text = user_fio
    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 45)
    text_size = font.getsize(text)
    position_second = text_size[0] + 250

    # drawing.rectangle(((220, 470), (780, 520)), fill="white", outline="black")
    drawing.rectangle(((220, 470), (text_size[0] + 250, 520)), fill="white", outline="black")
    drawing.text(pos, text, fill=black, font=font)

    black = (3, 8, 12)
    pos = (position_second + 30, 525)
    text = str(card_number)
    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 45)
    text_size = font.getsize(text)

    # drawing.rectangle(((220, 470), (780, 520)), fill="white", outline="black")
    drawing.rectangle(((position_second + 20, 520), (position_second + 200, 570)), fill="white", outline="black")
    drawing.text(pos, text, fill=black, font=font)

    photo.save(f"{card_number}.jpg")

    with open(f"{card_number}.jpg", "rb") as file:
        data = file.read()

    os.remove(f"{card_number}.jpg")

    return data


# Нажатие на кнопку Пригласить друга
# Генерация реферальных ссылок
# async def sum_approved_users(user_id):
async def sum_approved_users(user_id):
    info = await db.get_user_info(user_id)
    referral_id = info[0]['referral_id']
    all_invited_users = await db.get_all_invited_users(referral_id)

    users_activated_card = []
    approved_users = 0
    for user in all_invited_users:
        if user['card_status'] == True:
            users_activated_card.append("@" + user['username'] + " - Подтвержден")
            approved_users += 1
        else:
            users_activated_card.append("@" + user['username'] + " - Не подтвержден")

    return info, referral_id, approved_users, all_invited_users


@dp.message_handler(Text(contains="Пригласить друга"))
async def invite_friend(message: Message):
    user_id = message.from_user.id

    info, referral_id, approved_users, all_invited_users = await sum_approved_users(user_id=user_id)

    text = "Получи любую пиццу на выбор бесплатно в нашем ресторане \n\n Для этого нужно пригласить всего лишь 5 друзей \n\n✅ Используй любую из ссылок ниже, чтобы пригласить друзей в бота. Чтобы приглашение было Тебе засчитано, " \
           "приглашенный тобой пользователь должен оформить карту лояльности находясь в заведении!"

    await message.answer(text, reply_markup=cancel_btn)
    prizes = approved_users // 5 - info[0]["prize"]

    text = f"Получено подарков за приглашения: {info[0]['prize']}/{prizes + info[0]['prize']}\n\n" \
           f"Ты пригласил {str(len(all_invited_users))} человека в бота\n" \
           f"Подтверждённых приглашений (Оформили карту лояльности): {str(approved_users)}\n\n" \
           "Внутренняя ссылка: эту ссылку Ты можешь скидывать своим друзьям или выкладывать в чаты внутри экосистемы " \
           "Telegram:\n\n" \
           f"https://t.me/tgpb_bot?start={referral_id}\n\n" \
           "Внешняя ссылка: эту ссылку ты можешь скидывать своим друзьям во всех других соц. сетях, мессенджерах, " \
           "прикреплять в stories в Instagram и т.д.:\n\n" \
           f"https://tx.me/tgpb_bot?start={referral_id}\n\n"

    if prizes != 0:
        get_prize_inline.inline_keyboard[0][0]["callback_data"] = f"get_prize-{user_id}"
        await message.answer(text, reply_markup=get_prize_inline)
    else:
        await message.answer(text, reply_markup=menuUser)


# Показать активные коды скидок
@dp.message_handler(Text(contains="Мои подарки"))
async def get_active_codes(message: Message):
    # TODO: Протестить получение и обмен кодов
    user_id = message.from_user.id
    codes = await db.get_active_codes_user(user_id)

    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке

    if codes:
        text = "Ваши коды\n\n"
        text += "Для их использования Ты должен находиться в заведении\n"

        for code in codes:
            markup.add(InlineKeyboardButton(f"{str(code['code'])} - {code['code_description']}",
                                            callback_data=f"prize_code-{str(code['code'])}"))
    else:
        text = "К сожалению у Тебя нет призовых кодов"

    await message.answer(text=text, reply_markup=markup)


# Использовать призовые коды
@dp.callback_query_handler(text_contains=["prize_code"], state=None)
async def use_prize_code(call, state: FSMContext):
    await UsePrizeCode.use_prize.set()
    pc_info = await db.get_code_prize_info(int(call.data.split('-')[1]))

    async with state.proxy() as data:
        data["prize_code"] = int(call.data.split('-')[1])
        data["prize_desc"] = pc_info[0]["code_description"]
        data["prize_id"] = pc_info[0]["id"]

    if pc_info[0]['code_status'] == True:
        text = 'Введи номер столика и официант принисет Твой приз.\n\n'
        markup = cancel_btn
    else:
        text = 'К сожалению Ты уже использовал этот код!!!'
        await state.finish()
        markup = menuUser

    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer(text=text, reply_markup=markup)


# Использовать коды, ловим номер столика для вызова официантв
@dp.message_handler(content_types=["text"], state=UsePrizeCode.use_prize)
async def use_prize_code_waiter_call(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()

    text = f'Столик {message.text} (@{message.from_user.username}) заказал свой приз \n{data["prize_desc"]} - Код {data["prize_code"]}\n\n'
    await bot.send_message(chat_id=admins[0], text=text)
    await db.update_prize_code_status(data["prize_code"])

    text = "Официант уже на пути к Тебе"
    await message.answer(text=text, reply_markup=menuUser, parse_mode=types.ParseMode.HTML)


# Нажатие на кнопку получить приз
@dp.callback_query_handler(text_contains=["get_prize"])
async def get_user_prize(call):
    await call.answer(cache_time=60)
    cb_data = call.data.split('-')
    user_id = int(cb_data[1])

    info, referral_id, approved_users, all_invited_users = await sum_approved_users(user_id=user_id)
    prizes = approved_users // 5 - info[0]["prize"]

    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup="")

    text = "Вот Твои коды\n"
    while prizes != 0:
        id_code = await db.generate_prize_code(int(user_id))
        info = await db.get_user_info(int(user_id))
        print(info[0]['prize'])
        count_prize = info[0]['prize'] + 1
        await db.update_count_prize(int(user_id), count_prize)
        code_info = await db.get_code_prize(id_code)
        text += f"{code_info[0]['code']} - {code_info[0]['code_description']} \n\n "
        prizes -= 1

    text += f"Используй его из меню Программа лояльности - Мои Коды"

    await call.message.answer(text=text, reply_markup=menuUser)


# 1 шаг Фамилия Имя
@dp.message_handler(Text(contains="Оформить карту"), state=None)
async def reg_loyal_card(message: Message, state: FSMContext):
    info = await db.get_user_info(message.from_user.id)
    await CardLoyalReg.fio.set()

    if info[0]["card_status"] != True:
        # Введите Ваши имя и фамилию. Два слова.
        # Введите дату Вашего рождения в формате ДД.ММ.ГГГГ
        # Отправьте номер Вашего телефона нажав на кнопку ниже
        text = "<b>Шаг [1/4]</b>\n\n Введи свои имя и фамилию. Два слова."
        await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)
    else:
        await state.finish()
        text = "Вот твоя карточка. Используй её для получения скидок и участия в акциях."
        card = card_generate(info[0]["user_id"], info[0]["card_fio"], info[0]["card_number"])
        await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text, reply_markup=menuUser)


# Программа лояльности
# 2 шаг Дата рождения
@dp.message_handler(content_types=["text"], state=CardLoyalReg.fio)
async def reg_loyal_card_fio(message: types.Message, state: FSMContext):
    await CardLoyalReg.birthday.set()
    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
        data["card_fio"] = message.text

    text = "<b>Шаг [2/4]</b>\n\n Введи дату твоего рождения в формате ДД.ММ.ГГГГ (07.10.1985)"
    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)


# Программа лояльности
# 3 шаг Номер телефона
@dp.message_handler(content_types=["text"], state=CardLoyalReg.birthday)
async def reg_loyal_card_birthday(message: types.Message, state: FSMContext):
    try:
        data = message.text.split(".")
        data_cur = datetime.now()
        age = data_cur.year - int(data[2])
        if age < 18:
            text = "Прошу прощения, но карта лояльности выдается лицам старше 18 лет."
            await message.answer(text=text, reply_markup=menuUser)
            await state.finish()
            return
        else:
            if len(data) == 3:
                if (len(data[0]) == 2) and (len(data[1]) == 2) and (len(data[2]) == 4):
                    data = await state.get_data()
                    await CardLoyalReg.phone.set()

                    async with state.proxy() as data:
                        data["birthday"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()
                    text = "<b>Шаг [3/4]</b>\n\n Отправь свой номер телефона, нажав на кнопку ниже \n\n " \
                           "или введи в формате +77777777777\n\nНажми кнопку ниже⬇"
                    await message.answer(text, reply_markup=send_phone_cancel, parse_mode=types.ParseMode.HTML)

                else:
                    text = "Я Тебя не понимаю! Введи дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
                    await message.answer(text=text)
            else:
                text = "Я Тебя не понимаю! Введи дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
                await message.answer(text=text)
    except:
        text = "Я Тебя не понимаю! Введи дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
        await message.answer(text=text)


# Программа лояльности
# Проверка данных
@dp.message_handler(content_types=["contact", "text"], state=CardLoyalReg.phone)
async def reg_loyal_card_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()

    async with state.proxy() as data:
        if message.content_type == 'contact':
            if message.contact.phone_number[0] != "+":
                data["phone_number"] = "+" + message.contact.phone_number
            else:
                data["phone_number"] = message.contact.phone_number
        else:
            data["phone_number"] = message.text

    await CardLoyalReg.approve.set()

    text = "Проверь введенные данные:\n\n"
    text += f"Твои имя и фамилия: {data['card_fio']}\n"
    text += f"Твой день рождения: {data['birthday'].strftime('%m-%d-%Y')}\n"
    text += f"Твой номер телефона: {data['phone_number']}\n"

    await message.answer(text)

    await message.answer("Если всё правильно, подтверди", reply_markup=user_inline_approve)

    async with state.proxy() as data:
        data["msg_id"] = message.message_id

    await CardLoyalReg.approve.set()


# Картиа лояльности подтверждение изменение данных
@dp.callback_query_handler(text=["approve_order_user", "cancel_order_user"], state=CardLoyalReg.approve)
async def reg_loyal_card_approve(call, state: FSMContext):
    await call.answer(cache_time=60)

    if call.data == "approve_order_user":

        data = await state.get_data()
        info = await db.get_user_info(data["user_id"])

        if info[0]["card_status"] != True:
            await call.message.edit_text("Если всё правильно, подтверди", reply_markup="")

            await call.message.answer("⏳Ожидай подтверждения от администрации",
                                      reply_markup=menuUser)

            text = f"Пользователь @{info[0]['username']} оформил карту лояльности"

            # Сохранение данных в БД
            await db.update_user_data_card(data["user_id"], data["card_fio"], data["phone_number"], data["birthday"])

            admin_card_approve.inline_keyboard[0][0]["callback_data"] = f"admin_card_reject-{data['user_id']}"
            admin_card_approve.inline_keyboard[0][1]["callback_data"] = f"admin_card_approve-{data['user_id']}"
            await bot.send_message(chat_id=admins[0], text=text, reply_markup=admin_card_approve)

            await state.finish()
        else:
            card = card_generate(data["user_id"], data["card_fio"], data["card_number"])
            text = "Вот Твоя карточка. Используй её для получения скидок и участия в акциях."

            if call.message.from_user.id == int(admins[0]):
                await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                     reply_markup=menuAdmin)
            else:
                await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                     reply_markup=menuUser)

    elif call.data == "cancel_order_user":
        await state.finish()
        await call.message.edit_text("Исправь данные", reply_markup="")
        text = "<b>Шаг [1/3]</b>\n\n Введите свои имя и фамилию. Два слова."
        await call.message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

        await CardLoyalReg.fio.set()


# Картиа лояльности подверждение админом
@dp.callback_query_handler(text_contains=["admin_card_approve"])
async def reg_loyal_card_admin_approve(call, state: FSMContext):
    await call.answer(cache_time=60)

    cb_data = call.data.split('-')

    info = await db.get_user_info(int(cb_data[1]))
    text = f"Пользователь @{info[0]['username']} оформил карту лояльности"
    await call.message.edit_text(text=text, reply_markup="")
    card = card_generate(info[0]["user_id"], info[0]["card_fio"], info[0]["card_number"])

    if info[0]['card_status'] != True:

        # Активация карты лояльности
        await db.approve_user_card_admin(int(cb_data[1]))

        text = "Поздравляем! Ты стал участником программы лояльности.\n\n " \
               "Вот Твоя карточка. Используй её для получения скидок и участия в акциях."

        if call.message.from_user.id == int(admins[0]):
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuAdmin)
        else:
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuUser)

    else:
        text = "Вот Твоя карточка. Используй её для получения скидок и участия в акциях."

        if call.message.from_user.id == int(admins[0]):
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuAdmin)
        else:
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuUser)


# Отклонение карты администратором
@dp.callback_query_handler(text_contains=["admin_card_reject"])
async def reg_loyal_card_admin_reject(call):
    await call.answer(cache_time=60)

    cb_data = call.data.split('-')
    text = call.message.text
    await call.message.edit_text(text=text, reply_markup="")

    await bot.send_message(chat_id=cb_data[1], text="Твоя заявка на карту отклонена администрацией.")
