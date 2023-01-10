import os
from datetime import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from utils.db_api.db_commands import DBCommands

from keyboards.default.menu import *
from keyboards.inline.inline_buttons import admin_card_approve, user_inline_approve, get_prize_inline

from loader import dp, bot

from states.card_loyality import CardLoyalReg

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
@dp.message_handler(Text("Пригласить друга"))
async def invite_friend(message: Message):
    user_id = message.from_user.id
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

    text = "✅ Используйте любую из ссылок ниже, чтобы пригласить друзей в бота. Чтобы приглашение было вам засчитано, " \
           "приглашенный вами пользователь должен оформить карту лояльности находясь в заведении "

    await message.answer(text, reply_markup=cancel_btn)
    prizes = approved_users // 5 - info[0]["prize"]

    text = f"Получено подарков за приглашения: {info[0]['prize']}\n\n" \
           f"Вы пригласили {str(len(all_invited_users))} человека в бота\n" \
           f"Подтверждённых приглашений (Оформили карту лояльности): {str(approved_users)}\n\n" \
           "Внутренняя ссылка: эту ссылку вы можете скидывать своим друзьям или выкладывать в чаты внутри экосистемы " \
           "Telegram:\n\n" \
           f"https://t.me/tgpb_bot?start={referral_id}\n\n" \
           "Внешняя ссылка: эту ссылку вы можете скидывать своим друзьям во всех других соц. сетях, мессенджерах, " \
           "прикреплять в stories в Instagram и т.д.:\n\n" \
           f"https://tx.me/tgpb_bot?start={referral_id}\n\n"

    if prizes != 0:
        get_prize_inline.inline_keyboard[0][0]["callback_data"] = f"get_prize-{user_id}"
        await message.answer(text, reply_markup=get_prize_inline)
    else:
        await message.answer(text, reply_markup=menuUser)


# Показать активные коды скидок
@dp.message_handler(Text("Мои коды"))
async def get_active_codes(message: Message):
    user_id = message.from_user.id
    codes = await db.get_active_codes_user(user_id)
    if codes:
        text = "Ваши коды\n\n " \
               "Используйте их при записи на занятие, указав код в комментарии\n\n"
        for code in codes:
            text += str(code['code']) + " - " + code['code_description'] + "\n"
    else:
        text = "К сожалению у Вас нет призовых кодов"

    await message.answer(text=text, reply_markup=menuUser)


# Начало регистрации карты лояльности
@dp.message_handler(Text("Получить карту"), state=None)
async def reg_loyal_card(message: Message, state: FSMContext):
    info = await db.get_user_info(message.from_user.id)

    if info[0]["card_status"] != True:
        # Введите Ваши имя и фамилию. Два слова.
        # Введите дату Вашего рождения в формате ДД.ММ.ГГГГ
        # Отправьте номер Вашего телефона нажав на кнопку ниже
        text = "<b>Шаг [1/3]</b>\n\n Введите Ваши имя и фамилию. Два слова."
        await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

        await CardLoyalReg.fio.set()
    else:
        text = "Вот ваша карточка. Используйте её для получения скидок и участия в акциях."
        card = card_generate(info[0]["user_id"], info[0]["card_fio"], info[0]["card_number"])
        await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text, reply_markup=menuUser)


# Карта лояльности Фамилия и имя
@dp.message_handler(content_types=["text"], state=CardLoyalReg.fio)
async def reg_loyal_card_fio(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_id"] = message.from_user.id
        data["card_fio"] = message.text

    text = "<b>Шаг [2/3]</b>\n\n Введите дату Вашего рождения в формате ДД.ММ.ГГГГ (07.10.1985)"
    await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

    await CardLoyalReg.birthday.set()


# Карта лояльности дата рождения
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
                    async with state.proxy() as data:
                        data["birthday"] = datetime.strptime(message.text.replace(".", "-"), "%d-%m-%Y").date()
                    text = "<b>Шаг [3/3]</b>\n\n Отправьте номер Вашего телефона нажав на кнопку ниже \n\n " \
                           "или введите в формате +77777777777\n\nНажмите кнопку ниже⬇"
                    await message.answer(text, reply_markup=send_phone_cancel, parse_mode=types.ParseMode.HTML)

                    await CardLoyalReg.phone.set()
                else:
                    text = "Я Вас не понимаю! Введите дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
                    await message.answer(text=text)
            else:
                text = "Я Вас не понимаю! Введите дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
                await message.answer(text=text)
    except:
        text = "Я Вас не понимаю! Введите дату в правильном формате ДД.ММ.ГГГГ (07.10.1985)"
        await message.answer(text=text)


# Карта лояльности отправка контакта
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

    text = "Проверьте введенные данные:\n\n"
    text += f"Ваше имя и фамилия: {data['card_fio']}\n"
    text += f"Ваш день рождения: {data['birthday'].strftime('%m-%d-%Y')}\n"
    text += f"Ваш номер телефона: {data['phone_number']}\n"

    await message.answer(text)

    await message.answer("Если всё правильно, подтвердите", reply_markup=user_inline_approve)

    async with state.proxy() as data:
        data["msg_id"] = message.message_id

    await CardLoyalReg.approve.set()


# Картиа лояльности подтверждение изменение данных
@dp.callback_query_handler(text=["approve_staff_user", "cancel_staff_user"], state=CardLoyalReg.approve)
async def reg_loyal_card_approve(call, state: FSMContext):
    await call.answer(cache_time=60)

    if call.data == "approve_staff_user":

        data = await state.get_data()
        info = await db.get_user_info(data["user_id"])

        if info[0]["card_status"] != True:
            await call.message.edit_text("Если всё правильно, подтвердите", reply_markup="")

            await call.message.answer("⏳Ожидайте подтверждения от администрации",
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
            text = "Вот ваша карточка. Используйте её для получения скидок и участия в акциях."

            if call.message.from_user.id == int(admins[0]):
                await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                     reply_markup=menuAdmin)
            else:
                await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                     reply_markup=menuUser)

    elif call.data == "edit_staff_user":
        await state.finish()
        await call.message.edit_text("Исправьте данные", reply_markup="")
        text = "<b>Шаг [1/3]</b>\n\n Введите Ваши имя и фамилию. Два слова."
        await call.message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)

        await CardLoyalReg.fio.set()


# Картиа лояльности подверждение админом
# @dp.callback_query_handler(text=["admin_card_reject", "admin_card_approve"], state=CardLoyalReg.approve)
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

        text = "Поздравляем! Вы стали участником программы лояльности.\n\n " \
               "Вот ваша карточка. Используйте её для получения скидок и участия в акциях."

        if call.message.from_user.id == int(admins[0]):
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuAdmin)
        else:
            await bot.send_photo(chat_id=info[0]['user_id'], photo=card, caption=text,
                                 reply_markup=menuUser)

    else:
        text = "Вот ваша карточка. Используйте её для получения скидок и участия в акциях."

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

    await bot.send_message(chat_id=cb_data[1], text="Ваша заявка на карту отклонена администрацией.")


# Нажатие на кнопку получить приз
@dp.callback_query_handler(text_contains=["get_prize"])
async def get_user_prize(call):
    await call.answer(cache_time=60)
    cb_data = call.data.split('-')
    user_id = cb_data[1]

    await bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup="")

    info = await db.get_user_info(int(user_id))
    id_code = await db.generate_prize_code(int(user_id))

    count_prize = info[0]["prize"] + 1

    code_info = await db.get_code_prize(id_code)
    await db.update_count_prize(int(user_id), count_prize)

    text = f"Вот ваш код - {code_info[0]['code']} - {code_info[0]['code_description']} \n\n " \
           f"Используйте его при записи на занятие (Укажите в комментарии)"
    await call.message.answer(text=text, reply_markup=menuUser)
