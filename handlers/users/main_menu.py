from typing import Union

from handlers.users.user_order_shipping import build_category_keyboard
from loader import dp, bot
import re
from datetime import datetime

from aiogram import types
from keyboards.default import *
from keyboards.inline import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

from states.analytics import Analytics
from states.config import ConfigAdmins, MainMenu
from states.mailings import Mailings
from states.question import Question
from states.restoran import TableReservation
from states.reviews import Review
from states.shipping import Shipping


# Отмена действия
@dp.message_handler(Text(contains="Главное меню"), state="*")
async def cancel(message: types.Message, state=FSMContext):
    """Ловлю нажатие на кнопку Главное меню"""
    await db.update_last_activity(user_id=message.from_user.id, button='Главное меню')
    current_state = await state.get_state()

    data = await state.get_data()
    await message.delete()

    if str(message.from_user.id) in admins:
        await message.answer("Главное меню", reply_markup=menuAdmin)
    else:
        await message.answer("Главное меню", reply_markup=menuUser)

    if current_state == "MainMenu:main":
        if data != {}:
            await bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
        else:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)

    elif (re.search(r"ConfigAdmins:config_admins_", current_state)
          or re.search(r"ConfigBlackList:config_blacklist", current_state)
          or re.search(r"ConfigAdmins:config_main", current_state)
          or re.search(r"Mailings", current_state)
          or re.search(r"Analytics:main", current_state)):

        if data['id_msg_list']:
            for id_msg in data['id_msg_list']:
                try:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=id_msg)
                except Exception as ex:
                    pass

    await state.finish()
    await db.delete_cart(str(message.chat.id))


@dp.message_handler(Text(contains=["О ресторане"]))
async def menu(message: Message):
    """Обработчик нажатия на кнопку О Ресторане"""
    await db.update_last_activity(user_id=message.from_user.id, button='О ресторане')
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text)


@dp.message_handler(Text(contains=["Отзывы"]), state="*")
async def reviews(message: types.Message, state: FSMContext):
    """Стена с отзывами"""
    reviews = await db.get_approved_reviews()

    for item in reviews[-15:]:
        text = f"Отзыв оставил @{item['username']}\n"
        text += f"{item['text']}"
        await message.answer(text=text)
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(text="Оставить отзыв", callback_data="review")
    )
    await message.answer(text="Оставьте свой отзыв - Мы будем Вам благодарны 🤗", reply_markup=markup)


@dp.callback_query_handler(text="review", state="*")
async def new_review(call: types.CallbackQuery, state: FSMContext):
    """Нажатие на кнопку Оставить озыв"""
    await call.message.answer("Напишите Ваш отзыв")
    await Review.send_review.set()


@dp.message_handler(content_types=["text"], state=Review.send_review)
async def review_text(message: types.Message, state: FSMContext):
    """Ловлю текст отзыва и отправляю его на модерацию администратору"""
    await state.finish()

    text = "Благодарим Вас за обратную связь 🤗\n"
    text +="Ваш отзыв скоро появится на нашей стене"
    await message.answer(text=text)
    review_text = message.text.strip()
    username = message.from_user.username

    text = f"Пользователь @{username} оставил отзыв:\n"
    text = f"{review_text}"
    review_id = await db.add_new_review(text=review_text, username=username)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(text="Опубликовать", callback_data=f"approve_review-{review_id[0]['id']}"),
    )
    for admin in admins:
        await bot.send_message(chat_id=admin, text=text, reply_markup=markup)


@dp.callback_query_handler(text_contains=["approve_review"], state="*")
async def approve_review(call: types.CallbackQuery, state: FSMContext):
    """Одобрение отзыва администратором"""
    data = call.data.split('-')
    await db.update_status_review(id=int(data[-1]))
    await call.answer()


@dp.message_handler(Text(contains=["Меню"]), state="*")
async def menu(message: Message):
    """Обработчик нажатия на кнопку Меню"""
    await db.update_last_activity(user_id=message.from_user.id, button='Меню')
    text = f"Меню к Вашим услугам"
    msg = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    # await MainMenu.main.set()
    markup = await show_menu_buttons(message_id=msg.message_id + 1)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.message_handler(Text(contains=["Вызов персонала"]), state="*")
async def ansver_menu(message: Message):
    """Обработчик нажатия на кнопку вызов персонала"""
    await db.update_last_activity(user_id=message.from_user.id, button='Вызов персонала')
    text = f"Меню вызова персонала ниже"
    await MainMenu.main.set()
    await message.answer(text=text, reply_markup=menuPersonal)


@dp.callback_query_handler(text=["hall_reservation_mailings"], state="*")
@dp.message_handler(Text(contains="Забронировать стол"), state=None)
async def table_reservation(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    """Обработчик нажатия на кнопку Забронировать стол"""
    await db.update_last_activity(user_id=message.from_user.id, button='Забронировать стол')
    await TableReservation.data.set()

    date = datetime.now().strftime('%d.%m.%Y')
    text = f"<b>Шаг [1/5]</b>\n\n Введите дату в формате ДД.ММ.ГГГГ, сегодня {date}"
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)
    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.answer(text, reply_markup=cancel_btn, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text=["order_shipping_mailings"], state="*")
@dp.message_handler(Text(contains="Доставка"), state=None)
async def show_menu_order_shipping(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    """Обработчик нажатия на кнопку Оформить заказ на доставку"""
    await Shipping.main.set()
    if isinstance(message, types.Message):
        await db.update_last_activity(user_id=message.from_user.id, button='Оформить доставку')
        await db.delete_cart(str(message.chat.id))
        await message.delete()
        await message.answer('Оформление заказа на доставку', reply_markup=ReplyKeyboardRemove())
        message_id = message.message_id + 2
        user_id = message.from_user.id

    elif isinstance(message, types.CallbackQuery):
        call = message
        await db.update_last_activity(user_id=call.message.from_user.id, button='Оформить доставку')
        await db.delete_cart(str(call.message.chat.id))
        await call.message.edit_text('Оформление заказа на доставку')
        message_id = call.message.message_id + 2
        user_id = call.message.from_user.id

    await build_category_keyboard(message, state)

    async with state.proxy() as data:
        data["message_id"] = message_id
        data["chat_id"] = user_id


@dp.message_handler(Text(contains="Программа лояльности"), state=None)
async def reg_loyal_card(message: Message, state: FSMContext):
    """Обработчик нажатия на кнопку Программа лояльности"""
    await db.update_last_activity(user_id=message.from_user.id, button='Программа лояльности')
    info = await db.get_user_info(message.from_user.id)
    await MainMenu.main.set()
    if info[0]['card_status'] != True:
        text = "Оформите карту скидок!!!"
    else:
        text = "Меню программы лояльности"
    await message.delete()
    await message.answer(text, reply_markup=menuLoyality, parse_mode=types.ParseMode.HTML)


@dp.message_handler(Text(contains="Задайте нам вопрос"), state="*")
async def ask_question(message: Message, state: FSMContext):
    """Задайте нам вопрос"""
    await Question.ask_questions.set()
    await message.answer(text="Задайте Ваш вопрос", reply_markup=cancel_btn)


@dp.message_handler(content_types=["text"], state=Question.ask_questions)
async def send_question_to_admin(message: types.Message, state: FSMContext):
    """Ловлю вопрос от пользователя и отправляю его администратору"""
    question_text = message.text.strip()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="Ответить в ЛС", callback_data="", url=f"https://t.me/{message.from_user.username}")
    )

    text = f"Пользователь @{message.from_user.username} задает вопрос:\n"
    text += f"{question_text}\n"

    for admin in admins:
        await bot.send_message(chat_id=admin, text=text, reply_markup=markup)
    await state.finish()
    text = "Благодарим Вас за обратную связь 🤗. С Вами скоро свяжется наш администратор."
    if str(message.from_user.id) in admins:
        await message.answer(text=text, reply_markup=menuAdmin)
    else:
        await message.answer(text=text, reply_markup=menuUser)


@dp.message_handler(Text(contains="Акции"), state="*")
async def promotions(message: Message):
    """Лювлю нажатие на кнопку Акции"""
    await db.update_last_activity(user_id=message.from_user.id, button='Акции')
    text = f"https://teletype.in/@andreytikhonov/uJftR9aBA"
    await message.answer(text=text)


@dp.message_handler(Text(contains="Сделать рассылку подписчикам"), state="*")
async def newsletter(message: Message):
    """Лювлю нажатие на кнопку Сделать рассылку пользователям"""
    text = "Меню рассылки"
    await Mailings.main.set()
    await message.answer(text=text, reply_markup=newsletter_kbd)


@dp.message_handler(Text(contains=["Настройки"]), state="*")
async def admin_config(message: Message, state: FSMContext):
    """Ловлю нажатие на кнопку Настройки"""
    text = "Меню настроек"
    await ConfigAdmins.config_main.set()
    async with state.proxy() as data:
        data['id_msg_list'] = []
    await message.answer(text=text, reply_markup=menu_admin_config)


@dp.message_handler(Text(contains=["Аналитика"]), state="*")
async def analytics(message: Message, state: FSMContext):
    """Ловлю нажатие на кнопку Аналитика"""
    await message.delete()
    text = "Аналитика"
    await Analytics.main.set()
    async with state.proxy() as data:
        data['id_msg_list'] = []
    await message.answer(text=text, reply_markup=analytics_kbd)
