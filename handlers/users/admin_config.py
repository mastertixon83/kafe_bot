from loader import dp, bot
from data.config import admins
from utils.db_api.db_commands import DBCommands

from states.edit_menu import *
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from keyboards.default import *

from aiogram.dispatcher.filters import Text

from data.config import admins
from aiogram.dispatcher import FSMContext

db = DBCommands()


### Генерация клавиатуры
async def keiboard_generator(items, what, message: Message):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    msg_id_list = []

    for item in items:
        markup.inline_keyboard.clear()
        row = [
            InlineKeyboardButton("Редактировать", callback_data=f"edit-{what}-{str(item['id'])}"),
            InlineKeyboardButton("Удалить", callback_data=f"delete-{what}-{str(item['id'])}")
        ]
        markup.add().row(*row)
        msg = await message.answer(text=f"{str(item['title'])}", reply_markup=markup)
        msg_id_list.append(msg)
    chat_id = message.chat.id

    return msg_id_list, chat_id

async def delete_cat_msg_buttons(state: FSMContext):
    ### Удаление кнопок с категориями
    data = await state.get_data()
    for item in data['msg_id_list']:
        await bot.delete_message(chat_id=data['chat_id'], message_id=item['message_id'])
        await state.finish()
@dp.message_handler(Text("Добавить"), state="*")
async def test(message: Message, state: FSMContext):
    pass

# Редактирование категорий
@dp.message_handler(Text(["Категории", "Блюда"]))
async def admin_edit_categories(message: Message, state: FSMContext):
    text = f"Редактировать {message.text.lower()}"
    await message.delete()
    if message.text == "Категории":
        await EditCategory.list_categories.set()
        categories = await db.get_all_categories()
        msg_id_list, chat_id = await keiboard_generator(items=categories, what='category', message=message)

        async with state.proxy() as data:
            data['msg_id_list'] = msg_id_list
            data['chat_id'] = chat_id

    elif message.text == "Блюда":
        await EditItem.edit_item_select_category.set()
        text = "Выберите категорию, блюда в которой хотите редактировать"

        categories = await db.get_all_categories()

        markup = InlineKeyboardMarkup()

        for category in categories:
            row = [
                InlineKeyboardButton(f"{category['title']}", callback_data=f"category-{str(category['id'])}"),
            ]
            markup.add().row(*row)
        await message.answer(text=text, reply_markup=markup)
        return

    await message.answer(text=text, reply_markup=menu_admin_edit2)


### Редактирование категории или блюда
@dp.callback_query_handler(text_contains=["edit"])
async def admin_edit_category_item(call: types.CallbackQuery, state: FSMContext):
    call_data = call.data.split("-")

    async with state.proxy() as data:
        data['id'] = int(call_data[2])

    if call_data[1] == "category":
        await EditCategory.edit_category.set()
        info = await db.get_category_info(int(call_data[2]))
        text = f"Редактируем категорию {info[0]['title']} - Введите новое название"
        await call.message.answer(text=text)

    elif call_data[1] == "item":
        await EditItem.edit_item_select_category.set()
    await call.answer()


### Удалеие категории или блюда
@dp.callback_query_handler(text_contains=["delete"])
async def admin_delete_category_item(call, state: FSMContext):
    await call.answer(cache_time=10)
    call_data = call.data.split("-")

    if call_data[1] == "category":
        # await db.delete_category(int(call_data[2]))
        # text = f"Категория {} успешно удалена"
        print(call_data)
        print(call.data)

    elif call_data[1] == "item":
        # await EditItem.edit_item_title.set()
        print("Будем удалять блюдо")


# Редактирование категории
@dp.message_handler(content_types=["text"], state=EditCategory.edit_category)
async def edit_category_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await db.update_category(title=message.text, id=data['id'])

    await message.answer(text='Категория успешно изменена', reply_markup=menu_admin_edit)
    await state.finish()


# Редактирование блюда Название
@dp.message_handler(content_types=["text"], state=EditItem.edit_item_title)
async def edit_item_title(message: types.Message, state: FSMContext):
    await EditItem.edit_item_desc.set()

    async with state.proxy() as data:
        data['item_title'] = message.text


# Редактирование блюда Описание
@dp.message_handler(content_types=["text"], state=EditItem.edit_item_desc)
async def edit_item_desc(message: types.Message, state: FSMContext):
    await EditItem.edit_item_photo.set()

    async with state.proxy() as data:
        data['item_desc'] = message.text


# Редактирование блюда Фото
@dp.message_handler(content_types=["text"], state=EditItem.edit_item_photo)
async def edit_item_desc(message: types.Message, state: FSMContext):
    await EditItem.edit_item_price.set()

    async with state.proxy() as data:
        data['item_photo'] = message.text


# Редактирование блюда Цена
@dp.message_handler(content_types=["text"], state=EditItem.edit_item_price)
async def edit_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_price'] = message.text
    print(data)
    await state.finish()
