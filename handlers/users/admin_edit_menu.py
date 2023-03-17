import os
import re
from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from keyboards.default import cancel_btn, menuAdmin
from keyboards.inline.inline_admin_edit_menu import categories_keyboard, menu_cd, \
    items_in_category_keyboard, what_to_edit_keyboard, make_callback_data

from loader import dp, bot
from states.config import MainMenu
from utils.db_api.db_commands import DBCommands

url_pattern = re.compile(r'(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')

db = DBCommands()


@dp.message_handler(Text(contains=["Редактировать меню"]), state='*')
async def show_menu(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Редактировать меню"""
    await MainMenu.main.set()
    await message.delete()

    await message.answer('Редактирование меню', reply_markup=ReplyKeyboardRemove())

    await what_to_edit(message)

    async with state.proxy() as data:
        data["message_id"] = message.message_id + 2
        data["chat_id"] = message.from_user.id


@dp.callback_query_handler(menu_cd.filter(), state="*")
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Ловлю нажатие любой инлайн кнопки"""
    current_level = callback_data.get('level')
    category_id = callback_data.get('category_id')
    item_id = callback_data.get('item_id')
    action = callback_data.get('action')
    what = callback_data.get('what')
    st = state

    levels = {
        "-1": main_menu,
        "0": what_to_edit,
        "1": list_categories,
        "2": list_items_in_category,
        "3": edit_item,
        "12": new_category,
        "13": delete_category,
        "14": edit_position_category,
        "22": new_item,
        "23": delete_item
    }

    current_level_functions = levels[current_level]
    await current_level_functions(
        call,
        category_id=category_id,
        item_id=item_id,
        action=action,
        what=what,
        state=st
    )


async def main_menu(callback: types.CallbackQuery, what, state, **kwargs):
    """Ловлю нажатие кнопки выход"""
    await callback.message.delete()
    await callback.message.answer(text="Главное меню", reply_markup=menuAdmin)
    # await bot.send_message(chat_id=callback.message.from_user.id, text="Главное меню", reply_markup=menuUser)
    await state.finish()


async def what_to_edit(message: Union[types.Message, types.CallbackQuery], **kwargs):
    """Ловлю нажатие кнопки Что будем редактировать"""
    markup = await what_to_edit_keyboard()

    if isinstance(message, types.Message):
        await message.answer("Что будем редактировать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будем редактировать?", reply_markup=markup)


async def edit_position_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    """Ловлю нажатие на изменение позиции"""
    await MainMenu.edit_category_position.set()
    info = await db.get_category_info(id=int(category_id))

    async with kwargs['state'].proxy() as data:
        data['category_id'] = category_id

    if action == "edit_category_position":
        text = f"Текущая позиция {info[0]['position']}\n\nВведите позицию категории"
        await callback.message.edit_text(text=text)


@dp.message_handler(content_types=["text"], state=MainMenu.edit_category_position)
async def category_position(message: types.Message, state: FSMContext):
    """Ловлю позицию категории"""
    data = await state.get_data()

    await db.update_category_position(position=int(message.text), id=int(data['category_id']))
    await message.delete()

    await MainMenu.main.set()
    markup = await categories_keyboard(what='category')

    await bot.edit_message_text(text="Какую категорию будем изменять?", chat_id=message.chat.id, message_id=data['message_id'])
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['message_id'], reply_markup=markup)


async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    """Нажатие на кнопку Категории и вывод всех категорий меню"""
    markup = await categories_keyboard(kwargs['what'])
    text = "Какую категорию будем изменять?"
    if isinstance(message, types.Message):
        await message.edit_text(text=text, reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text=text, reply_markup=markup)


async def list_items_in_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    """Нажатие на категорию, вывод блюд в данной категории, редактирование категории"""
    info = await db.get_category_info(id=int(category_id))
    count_items = await db.get_all_items_in_category(category_id=int(category_id))

    if action == "edit_items":

        markup = await items_in_category_keyboard(int(category_id))
        if markup == None:

            markup = InlineKeyboardMarkup()
            markup.row(
                        InlineKeyboardButton(
                                            text="Назад",
                                            callback_data=make_callback_data(level=1,
                                                                            category_id=category_id,
                                                                            what='items'
                                                                            )
                                            )
                        )
            await callback.message.edit_text(f"В категории {info[0]['title']} еще не добвлено блюд",
                                             reply_markup=markup)
        else:
            if len(count_items) == 0:
                text = f"В категории {info[0]['title']} еще не добвлено блюд"
            else:
                text = f"Выбрана категория {info[0]['title']} \nКакое блюдо будем редактировать?"
            await callback.message.edit_text(text=text, reply_markup=markup)

    elif action == "edit_category_position":

        async with kwargs['state'].proxy() as data:
            data['category_id'] = category_id
            data['action'] = action

        info = await db.get_category_info(id=int(category_id))

        await callback.message.edit_text(text=f"Введите новое название категории - {info[0]['title']}")
        await MainMenu.category_title.set()


async def delete_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    """Ловлю нажатие на кнопку удалить категорию"""
    await db.delete_category(id=int(category_id))
    await list_categories(callback.message, what='category')


async def new_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    """Ловлю нажатие на кнопку добавьт новую категорию - Редактирование"""
    await MainMenu.category_title.set()

    async with kwargs['state'].proxy() as data:
        if action == "edit_category_position": data['category_id'] = category_id
        data['action'] = action

    text = "<b>ШАГ [1/2]</b>Введите название категории"
    await callback.message.edit_text(text=text)


@dp.message_handler(content_types=["text"], state=MainMenu.category_title)
async def category_title(message: types.Message, state: FSMContext):
    """Ловлю Название категории"""
    await MainMenu.category_url.set()

    async with state.proxy() as data:
        data['title'] = message.text

    await message.delete()

    text = "<b>ШАГ [2/2]</b>Введите ссылку на меню категории"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=["text"], state=MainMenu.category_url)
async def category_url(message: types.Message, state: FSMContext):
    """Ловлю URL категории"""
    await message.delete()
    data = await state.get_data()

    match = re.search(url_pattern, message.text)
    if match:
        url = match.group(0)
        if data['action'] == "edit_category_position":
            await db.update_category(title=data['title'], id=int(data['category_id']), url=message.text)
        elif data['action'] == "new_category":
            await db.add_new_category(title=data['title'], url=url)

        await MainMenu.main.set()
        markup = await categories_keyboard(what='category')

        text = "Какую категорию будем редактировать?"
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data['message_id'], text=text)
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['message_id'], reply_markup=markup)

    else:

        text = "Введена не ссылка\n\n"
        text += "<b>ШАГ [2/2]</b>Введите ссылку на меню категории"
        await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


async def edit_item(callback: types.CallbackQuery, item_id, category_id, action, state, **kwargs):
    """Ловлю нажатие на кнопку блюда - Редктирование"""
    await MainMenu.item_title.set()
    data = await state.get_data()

    async with state.proxy() as data:
        data["item_id"] = item_id
        data["category_id"] = category_id
        data['action'] = action

    item = await db.get_item_info(int(item_id))
    text = f"Редактирование <b>{item[0]['title']}</b>\n\n"
    text += f"Описание\n\n"
    text += f"{item[0]['description']}\n"
    text += f"Цена: {item[0]['price']}\n\n"
    text += "<b>ШАГ [1/4]</b>Введи название блюда"
    await callback.message.edit_text(text=text)
    # await bot.edit_message_text(text=text, chat_id=callback.message.from_user.id, message_id=data['message_id'])


async def new_item(callback: types.CallbackQuery, action, category_id, **kwargs):
    """Нажатие на кнопку добавить новое блюдо"""
    await MainMenu.item_title.set()
    async with kwargs['state'].proxy() as data:
        data['category_id'] = category_id
        data['action'] = action

    text = "<b>ШАГ [1/4]</b>Введите название блюда"
    await callback.message.edit_text(text=text)


@dp.message_handler(content_types=["text"], state=MainMenu.item_title)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    """Ловлю название блюда"""
    await MainMenu.item_desc.set()

    async with state.proxy() as data:
        data['title'] = message.text

    await message.delete()

    text = "<b>ШАГ [2/4]</b>Введите описание блюда"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=["text"], state=MainMenu.item_desc)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    """Ловлю описание блюда"""
    await MainMenu.item_price.set()

    async with state.proxy() as data:
        data['desc'] = message.text

    await message.delete()

    text = "<b>ШАГ [3/4]</b>Введите цену блюда"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=["text"], state=MainMenu.item_price)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    """Ловлю цену блюда"""
    await message.delete()

    if message.text.isdigit():
        async with state.proxy() as data:
            data['price'] = message.text
        text = "<b>ШАГ [4/4]</b>Загрузите изображение блюда"
        await MainMenu.item_photo.set()
    else:
        text = "Введена некорректную сумма\n\n"
        text += "<b>ШАГ [3/4]</b>Введите цену блюда"

    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(lambda message: not message.photo, state=MainMenu.item_photo)
async def check_photo(message: types.Message, state: FSMContext):
    """Проверяю сообщение на тип, картинка или нет"""
    await message.delete()

    data = await state.get_data()
    text = "Это не фотография!\n\n"
    text += "<b>ШАГ [4/4]</b>Загрузите изображение блюда"

    return await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=types.ContentType.PHOTO, state=MainMenu.item_photo)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    """Ловлю изображение блюда"""
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id

    try:
        await message.photo[-1].download(f'media/menu/{data["photo"]}.jpg')
    except Exception as _ex:
        os.mkdir("media/menu")
        await message.photo[-1].download(f'media/menu/{data["photo"]}.jpg')

    data = await state.get_data()

    title = data['title']
    description = data['desc']
    price = data['price']
    photo = data['photo']
    category_id = data["category_id"]

    if data["action"] == "new_item":
        record_id = await db.add_new_dish(
            title=title,
            description=description,
            price=float(price),
            photo=photo,
            category_id=category_id
        )

    elif data["action"] == "edit_item":
        item_id = data['item_id']

        await db.update_dish(title=title, description=description, price=float(price), photo=photo,
                             item_id=int(item_id))

    info = await db.get_category_info(id=int(category_id))

    markup = await items_in_category_keyboard(int(category_id))
    text = f"Выбрана категория <b>{info[0]['title']}</b> \nКкое блюдо будем редактировать?"

    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'], reply_markup=markup)

    await MainMenu.main.set()


async def delete_item(callback: types.CallbackQuery, item_id, category_id, **kwargs):
    """Ловлю нажатие на кнопку Удалить блюдо"""
    await db.delete_item(id=int(item_id))

    await list_items_in_category(callback=callback, category_id=int(category_id), action='edit_items', kwargs=kwargs)
