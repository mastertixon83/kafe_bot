#TODO: Написать инструкцию по пользованию ботом
#TODO: !!!Сделать логирование

from keyboards.inline.dating_ikb import user_gender_ikb, user_work_ikb
from loader import dp, bot, db, logger

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
from keyboards.default import menuUser, menuAdmin
from aiogram.dispatcher.filters.builtin import CommandStart
from data.config import admins
from aiogram.dispatcher import FSMContext

from utils.db_api.db_commands import DBCommands
from states.dating import Dating

db = DBCommands()


@dp.message_handler(commands=['start'], state="*")
async def bot_start(message: types.Message, state: FSMContext):
    user_info = await db.get_user_info(message.from_user.id)
    user_id = str(message.from_user.id)

    if not user_info:
        if message.from_user.username == None:
            text = "Мы рады преветствовать Вас в нашем чат-боте.\n" \
                   "В Вашем профиле не указано имя пользователя.\n" \
                   "Для правильной работы бота это необходимо сделать. \n\n " \
                   "‼️‼️‼️ Для этого зайдите в настройки своего профиля и введите имя пользователя, после этого нажмите /start в боте"

            await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
            return
        current_state = await state.get_state()
        if current_state is None:
            pass
        else:
            await state.finish()

        user_id = message.from_user.id
        await Dating.user_gender.set()

        text = "👋👋👋👋 Рад приветствовать Вас.\n"
        text += 'Я виртуальный помошник ресторана "Долма"\n\n'
        text += "Давайте познакомимся поближе\n"
        text += "Кто вы?"
        msg = await message.answer(text=text, reply_markup=user_gender_ikb)
        try:
            args = message.get_args()
        except Exception:
            args = ""
        async with state.proxy() as data:
            data['user_id'] = user_id
            data['args'] = args
            data['msg_id'] = msg.message_id

    else:
        if user_id in admins:
            markup = menuAdmin
        else:
            markup = menuUser

        await message.answer("Глвное меню", reply_markup=markup)
        await state.finish()
        try:
            await db.update_last_activity(user_id=message.from_user.id, button='Команда старт')
        except Exception as _ex:
            logger.error(_ex)


@dp.callback_query_handler(text=["ug_female", "ug_male"], state=Dating.user_gender)
async def user_gender(call: types.CallbackQuery, state: FSMContext):
    """Ловлю выбор пола пользователем"""

    await Dating.user_age.set()

    if call.data == "ug_female":
        gender = "f"
    elif call.data == "ug_male":
        gender = "m"

    async with state.proxy() as data:
        data['gender'] = gender

    text = "Здорово 😊\n\n"
    text += "Укажите к какой возрастной категории Вы относитесь"
    await call.message.edit_text(text=text)
    msg = await call.message.edit_reply_markup(reply_markup=user_work_ikb)


@dp.callback_query_handler(text=["20-30", "30-40", "40-50", "50+"], state=Dating.user_age)
async def user_work(call: types.CallbackQuery, state: FSMContext):
    """Ловлю выбор занятости пользователем"""
    if call.data == "20-30":
        age_group = "20-30"
    elif call.data == "30-40":
        age_group = "30-40"
    elif call.data == "40-50":
        age_group = "40-50"
    elif call.data == "50+":
        age_group = "50+"

    async with state.proxy() as data:
        data['age_group'] = age_group

    data = await state.get_data()

    try:
        args = data['args']
    except Exception as _ex:
        args = ""
    if args == "":
        id_user = await db.add_new_user(gender=data['gender'], age_group=data['age_group'])
    else:
        id_user = await db.add_new_user(referral=args, gender=data['gender'],
                                        age_group=data['age_group'])

    try:
        await bot.delete_message(chat_id=call.message.from_user.id, message_id=data['msg_id'])
    except Exception as _ex:
        logger.error(_ex)

    text = "Отлично! Для получения скидки 10% остался лишь один шаг. Перейдите в меню программы лояльности и оформите карту 💳"
    if id in admins:
        await call.message.edit_text(text=text)
        text = "Если кнопки меню скрыты, то нажмите на иконку 🎛 в првом нижнем углу"
        await call.message.answer(text=text, reply_markup=menuAdmin)
    else:
        await call.message.edit_text(text=text)
        text = "Если кнопки меню скрыты, то нажмите на иконку 🎛 в првом нижнем углу"
        await call.message.answer(text=text, reply_markup=menuUser)

    await state.finish()
