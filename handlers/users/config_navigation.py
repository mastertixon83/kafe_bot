from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default import cancel_btn
from keyboards.inline.inline_admin_edit_menu import categories_keyboard, menu_cd, \
    items_in_category_keyboard, what_to_edit_keyboard, make_callback_data

from loader import dp, bot
from states.navigation import MainMenu
from utils.db_api.db_commands import DBCommands

db = DBCommands()


@dp.message_handler(Text(equals=["Редактировать меню"]), state='*')
async def show_menu(message: types.Message, state: FSMContext):
    await MainMenu.main.set()
    await message.answer('Редактирование меню', reply_markup=cancel_btn)
    await what_to_edit(message)
    async with state.proxy() as data:
        data["message_id"] = message.message_id + 2
        data["chat_id"] = message.from_user.id


###Ловлю нажатие любой инлайн кнопки
@dp.callback_query_handler(menu_cd.filter(), state="*")
async def navigate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get('level')
    category_id = callback_data.get('category_id')
    item_id = callback_data.get('item_id')
    message_id = callback_data.get('message_id')
    action = callback_data.get('action')
    what = callback_data.get('what')
    st = state

    levels = {
        "0": what_to_edit,
        "1": list_categories,
        "2": list_items_in_category,
        # "3": show_item,
        "12": edit_category,
        "22": edit_item
    }

    current_level_functions = levels[current_level]
    await current_level_functions(
        call,
        category_id=category_id,
        item_id=item_id,
        message_id=message_id,
        action=action,
        what=what,
        state=st
    )


async def what_to_edit(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await what_to_edit_keyboard()

    await MainMenu.what_to_edit.set()

    if isinstance(message, types.Message):
        await message.answer("Что будете редактировать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будете редактировать?", reply_markup=markup)
        # await call.message.edit_reply_markup(markup)


### Нажатие на кнопку Категории и вывод всех категори меню
async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard(kwargs['what'])
    await MainMenu.edit_new_category_title.set()
    data = await kwargs['state'].get_data()
    print(data)

    if isinstance(message, types.Message):
        await message.answer("Какую категорию Вы хотите изменить?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Какую категорию Вы хотите изменить?", reply_markup=markup)
        # await call.message.edit_reply_markup(markup)


### Нажатие на категорию и вывод блюд в данной категории
async def list_items_in_category(callback: types.CallbackQuery, category_id, **kwargs):

    if kwargs["action"] == "edit_items":
        markup = await items_in_category_keyboard(int(category_id))
        if markup == None:
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=1))
            )
            await callback.message.edit_text("В данной категории еще не добвлено блюд", reply_markup=markup)
        else:
            await callback.message.edit_text("Какое блюдо Вы хотите отредактировать?", reply_markup=markup)
    elif kwargs["action"] == "edit_category":
        print("Редактирование категории")
        await MainMenu.edit_new_category_title.set()


### Нажатие на кнопку добавить блюдо
async def edit_item(callback: types.CallbackQuery, item_id, action, **kwargs):
    await MainMenu.edit_new_item_title.set()
    if action == "new_item":
        print("Добавление нового блюда")
    #
    # item = await db.get_item_info(int(item_id))
    # text = f"Редактирование <b>{item[0]['title']}</b>\n\n"
    # text += f"Описание\n\n"
    # text += f"{item[0]['description']}\n"
    # text += f"Цена: {item[0]['price']}\n\n"
    # text += "<b>ШАГ [1/4]</b>Введите название блюда"
    # await callback.message.edit_text(text=text)


### Нажатие на кнопку Добавить категорию
async def edit_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await MainMenu.edit_new_category_title.set()
    async with kwargs['state'].proxy() as data:
        data["count_mans"] = 234
    print(data)
    if action == "new_category":
        print("Добавление новой категории")
    # category_info = await db.get_category_info(int(category_id))
    # text = f"Редактирование <b>{category_info[0]['title']}</b>\n\n"
    # text += "<b>ШАГ [1/1]</b>Введите новое название категории"
    # await callback.message.edit_text(text=text)





### Ловлю название блюда
@dp.message_handler(content_types=["text"], state=MainMenu.edit_new_item_title)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.edit_new_item_desc.set()
    async with state.proxy() as data:
        data['title'] = message.text

    text = "<b>ШАГ [2/4]</b>Введите описание блюда"
    await message.answer(text=text)


### Ловлю описание блюда
@dp.message_handler(content_types=["text"], state=MainMenu.edit_new_item_desc)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.edit_new_item_price.set()
    async with state.proxy() as data:
        data['desc'] = message.text

    text = "<b>ШАГ [3/4]</b>Введите цену блюда"
    await message.answer(text=text)


### Ловлю цену блюда
@dp.message_handler(content_types=["text"], state=MainMenu.edit_new_item_price)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.edit_new_item_photo.set()
    async with state.proxy() as data:
        data['price'] = message.text

    text = "<b>ШАГ [4/4]</b>Загрузите изображение блюда"
    await message.answer(text=text)


### Ловлю изображение блюда
@dp.message_handler(content_types=types.ContentType.PHOTO, state=MainMenu.edit_new_item_photo)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.edit_new_item_photo.set()
    print(message.photo[-1].file_id)
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
    await message.photo[-1].download(f'media/{data["photo"]}.jpg')
    text = f"Готово\n\n{data}"
    await message.answer(text=text)
