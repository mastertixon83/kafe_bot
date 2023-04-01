#TODO: Кнопка с геолокацией, проложить маршрут до ресторана
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
from aiogram import exceptions

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

        try:
            for id_msg in data['id_msg_list']:
                try:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=id_msg)
                except exceptions.MessageToDeleteNotFound:
                    pass
        except KeyError:
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
    """Обработчик нажатия на кнопку Доставка и кнопку Доставка из рассылки"""
    await Shipping.main.set()

    if isinstance(message, types.Message):
        ### Переход с главного меню
        user_id = message.from_user.id
        await db.delete_cart(str(message.chat.id))
        await message.delete()
        await message.answer('Оформление заказа на доставку', reply_markup=ReplyKeyboardRemove())
        user_id = message.from_user.id

    elif isinstance(message, types.CallbackQuery):
        ### Переход по кнопке из рассылки
        call = message
        user_id = call.message.from_user.id
        await db.delete_cart(str(call.message.chat.id))

    await db.update_last_activity(user_id=user_id, button='Оформить доставку')
    await build_category_keyboard(message, state)


@dp.message_handler(Text(contains="Программа лояльности"), state="*")
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
        InlineKeyboardButton(text="Ответить", callback_data=f"answer_to_user-{message.from_user.id}-{message.message_id}")
    )

    text = f"Пользователь @{message.from_user.username} задает вопрос:\n"
    text += f"{question_text}\n"

    for admin in admins:
        await bot.send_message(chat_id=admin, text=text, reply_markup=markup)
    await state.finish()
    text = "Благодарим Вас за обратную связь 🤗. Вам скоро ответят."
    if str(message.from_user.id) in admins:
        await message.answer(text=text, reply_markup=menuAdmin)
    else:
        await message.answer(text=text, reply_markup=menuUser)


@dp.callback_query_handler(text_contains=["answer_to_user"], state="*")
async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
    """Ответ пользователю на вопрос"""
    await Question.admin_answer.set()

    text="Введите ваш ответ"
    await call.message.answer(text=text)

    async with state.proxy() as data:
        data['user_id'] = call.data.split('-')[-2]
        data['message_id'] = call.data.split('-')[-1]


@dp.message_handler(content_types=["text"], state=Question.admin_answer)
async def send_answer_to_user(message: Message, state: FSMContext):
    """Ловлю ответ администратора и отправляю его пользователю задавшему вопрос"""
    data = await state.get_data()
    answer = message.text.strip()
    await bot.send_message(chat_id=int(data['user_id']), reply_to_message_id=int(data['message_id']), text=answer)
    await state.finish()
    await MainMenu.main.set()


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
