import re
from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.default import cancel_btn
from keyboards.inline.inline_admin_edit_menu import categories_keyboard, menu_cd, \
    items_in_category_keyboard, what_to_edit_keyboard, make_callback_data

from loader import dp, bot
from states.config import MainMenu
from utils.db_api.db_commands import DBCommands

url_pattern = re.compile(r'(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')

db = DBCommands()


@dp.message_handler(Text(equals=["Редактировать меню"]), state='*')
async def show_menu(message: types.Message, state: FSMContext):
    await MainMenu.main.set()
    await message.delete()

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
    action = callback_data.get('action')
    what = callback_data.get('what')
    st = state

    levels = {
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


async def what_to_edit(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await what_to_edit_keyboard()

    if isinstance(message, types.Message):
        await message.answer("Что будете редактировать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будете редактировать?", reply_markup=markup)


### Ловлю нажатие на изменение позиции
async def edit_position_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await MainMenu.edit_category_position.set()
    info = await db.get_category_info(id=int(category_id))

    async with kwargs['state'].proxy() as data:
        data['category_id'] = category_id

    if action == "edit_position":
        text = f"Текущая позиция {info[0]['position']}\n\nВведите позицию категории"
        await callback.message.edit_text(text=text)


### Ловлю позицию категории
@dp.message_handler(content_types=["text"], state=MainMenu.edit_category_position)
async def category_position(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await db.update_category_position(position=int(message.text), id=int(data['category_id']))
    await message.delete()

    await MainMenu.main.set()
    markup = await categories_keyboard(what='category')

    await bot.edit_message_text(text="Какую категорию Вы хотите изменить?", chat_id=message.chat.id, message_id=data['message_id'])
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['message_id'], reply_markup=markup)


### Нажатие на кнопку Категории и вывод всех категорий меню
async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard(kwargs['what'])

    if isinstance(message, types.Message):
        await message.edit_text("Какую категорию Вы хотите изменить?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Какую категорию Вы хотите изменить?", reply_markup=markup)


### Нажатие на категорию, вывод блюд в данной категории, редактирование категории
async def list_items_in_category(callback: types.CallbackQuery, category_id, action, **kwargs):
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
                text = f"Вы выбрали категорию {info[0]['title']} \nКакое блюдо Вы хотите отредактировать?"
            await callback.message.edit_text(text=text, reply_markup=markup)

    elif action == "edit_category":

        async with kwargs['state'].proxy() as data:
            data['category_id'] = category_id
            data['action'] = action

        info = await db.get_category_info(id=int(category_id))

        await callback.message.edit_text(text=f"Введите новое название категории - {info[0]['title']}")
        await MainMenu.category_title.set()


### Ловлю нажатие на кнопку удалить категорию
async def delete_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await db.delete_category(id=int(category_id))
    await list_categories(callback.message, what='category')


# ### Ловлю нажатие на кнопку добавьт новую категорию - Редактирование
async def new_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await MainMenu.category_title.set()

    async with kwargs['state'].proxy() as data:
        if action == "edit_category": data['category_id'] = category_id
        data['action'] = action

    text = "<b>ШАГ [1/2]</b>Введите название категории"
    await callback.message.edit_text(text=text)


### Ловлю Название категории
@dp.message_handler(content_types=["text"], state=MainMenu.category_title)
async def category_title(message: types.Message, state: FSMContext):
    await MainMenu.category_url.set()

    async with state.proxy() as data:
        data['title'] = message.text

    await message.delete()

    text = "<b>ШАГ [2/2]</b>Введите ссылку на категорию"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


### Ловлю URL категории
@dp.message_handler(content_types=["text"], state=MainMenu.category_url)
async def category_url(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()

    match = re.search(url_pattern, message.text)
    if match:
        url = match.group(0)
        if data['action'] == "edit_category":
            await db.update_category(title=data['title'], id=int(data['category_id']), url=message.text)
        elif data['action'] == "new_category":
            await db.add_new_category(title=data['title'], url=url)

        await MainMenu.main.set()
        markup = await categories_keyboard(what='category')

        text = "Какую категорию Вы хотите изменить?"
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data['message_id'], text=text)
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['message_id'], reply_markup=markup)

    else:

        text = "Вы ввели не ссылку!!! \n\n"
        text += "<b>ШАГ [2/2]</b>Введите ссылку на категорию"
        await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


### Ловлю нажатие на кнопку блюда - Редктирование
async def edit_item(callback: types.CallbackQuery, item_id, category_id, action, **kwargs):
    await MainMenu.item_title.set()

    async with kwargs["state"].proxy() as data:
        data["item_id"] = item_id
        data["category_id"] = category_id
        data['action'] = action

    item = await db.get_item_info(int(item_id))
    text = f"Редактирование <b>{item[0]['title']}</b>\n\n"
    text += f"Описание\n\n"
    text += f"{item[0]['description']}\n"
    text += f"Цена: {item[0]['price']}\n\n"
    text += "<b>ШАГ [1/4]</b>Введите название блюда"
    await bot.edit_message_text(text=text, chat_id=callback.message.from_user.id, message_id=data['message_id'])


### Нажатие на кнопку добавить новое блюдо
async def new_item(callback: types.CallbackQuery, action, category_id, **kwargs):
    await MainMenu.item_title.set()
    async with kwargs['state'].proxy() as data:
        data['category_id'] = category_id
        data['action'] = action

    text = "<b>ШАГ [1/4]</b>Введите название блюда"
    await callback.message.edit_text(text=text)


### Ловлю название блюда
@dp.message_handler(content_types=["text"], state=MainMenu.item_title)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.item_desc.set()

    async with state.proxy() as data:
        data['title'] = message.text

    await message.delete()

    text = "<b>ШАГ [2/4]</b>Введите описание блюда"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


### Ловлю описание блюда
@dp.message_handler(content_types=["text"], state=MainMenu.item_desc)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.item_price.set()

    async with state.proxy() as data:
        data['desc'] = message.text

    await message.delete()

    text = "<b>ШАГ [3/4]</b>Введите цену блюда"
    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


### Ловлю цену блюда
@dp.message_handler(content_types=["text"], state=MainMenu.item_price)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await message.delete()

    if message.text.isdigit():
        async with state.proxy() as data:
            data['price'] = message.text
        text = "<b>ШАГ [4/4]</b>Загрузите изображение блюда"
        await MainMenu.item_photo.set()
    else:
        text = "Вы ввели некорректную сумму\n\n"
        text += "<b>ШАГ [3/4]</b>Введите цену блюда"

    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


### Ловлю изображение блюда
@dp.message_handler(lambda message: not message.photo, state=MainMenu.item_photo)
async def check_photo(message: types.Message, state: FSMContext):
    await message.delete()

    data = await state.get_data()
    text = "Это не фотография!\n\n"
    text += "<b>ШАГ [4/4]</b>Загрузите изображение блюда"

    return await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'])


@dp.message_handler(content_types=types.ContentType.PHOTO, state=MainMenu.item_photo)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await message.delete()

    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id

    await message.photo[-1].download(f'media/{data["photo"]}.jpg')

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
    text = f"Вы выбрали категорию <b>{info[0]['title']}</b> \nКакое блюдо Вы хотите отредактировать?"

    await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=data['message_id'], reply_markup=markup)

    await MainMenu.main.set()

### Ловлю нажатие на кнопку удалить блюдо
async def delete_item(callback: types.CallbackQuery, item_id, category_id, **kwargs):

    await db.delete_item(id=int(item_id))

    await list_items_in_category(callback=callback, category_id=int(category_id), action='edit_items', kwargs=kwargs)
