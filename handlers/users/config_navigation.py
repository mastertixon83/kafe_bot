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
        "3": edit_item,
        "12": edit_category,
        "13": delete_category,
        "22": new_item,
        "23": delete_item
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

    if isinstance(message, types.Message):
        await message.answer("Что будете редактировать?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Что будете редактировать?", reply_markup=markup)


### Нажатие на кнопку Категории и вывод всех категорий меню
async def list_categories(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await categories_keyboard(kwargs['what'])

    if isinstance(message, types.Message):
        await message.answer("Какую категорию Вы хотите изменить?", reply_markup=markup)

    elif isinstance(message, types.CallbackQuery):
        call = message
        await call.message.edit_text(text="Какую категорию Вы хотите изменить?", reply_markup=markup)
        # await call.message.edit_reply_markup(markup)


### Нажатие на категорию, вывод блюд в данной категории, редактирование категории
async def list_items_in_category(callback: types.CallbackQuery, category_id, **kwargs):
    info = await db.get_category_info(id=int(category_id))
    if kwargs["action"] == "edit_items":
        markup = await items_in_category_keyboard(int(category_id))
        if markup == None:

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=1,
                                                                                    category_id=category_id,
                                                                                    what='items'
                                                                                    )
                                     )
            )
            await callback.message.edit_text(f"В категории {info[0]['title']} еще не добвлено блюд", reply_markup=markup)
        else:
            await callback.message.edit_text(f"Вы выбрали категорию {info[0]['title']} \nКакое блюдо Вы хотите отредактировать?", reply_markup=markup)

    elif kwargs["action"] == "edit_category":
        data = await kwargs['state'].get_data()

        async with kwargs['state'].proxy() as data:
            data['category_id'] = category_id

        await bot.delete_message(chat_id=callback.message.chat.id, message_id=data['message_id'])
        info = await db.get_category_info(id=int(category_id))

        await callback.message.answer(text=f"Введите новое название категории - {info[0]['title']}")
        await MainMenu.edit_category.set()


### Ловлю нажатие на кнопку удалить категорию
async def delete_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await db.delete_category(id=int(category_id))
    data = await kwargs['state'].get_data()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=data['message_id'])
    await list_categories(callback.message, what='category')


### Ловлю нажатие на кнопку категории - Редактирование
async def edit_category(callback: types.CallbackQuery, category_id, action, **kwargs):
    await MainMenu.new_category.set()
    if action == "new_category":
        text = "<b>ШАГ [1/1]</b>Введите название категории"
        await callback.message.edit_text(text=text)


### Ловлю Название категории
@dp.message_handler(content_types=["text"], state=[MainMenu.edit_category, MainMenu.new_category])
async def category_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state == "MainMenu:edit_category":
        await db.update_category(title=message.text, id=int(data['category_id']))
    elif current_state == "MainMenu:new_category":
        await db.add_new_category(title=message.text)

    await MainMenu.main.set()
    markup = await categories_keyboard(what='category')

    await message.answer("Какую категорию Вы хотите изменить?", reply_markup=markup)
    async with state.proxy() as data:
        data['message_id'] = message.message_id + 1


### Ловлю нажатие на кнопку блюда - Редктирование
async def edit_item(callback: types.CallbackQuery, item_id, action, **kwargs):
    await MainMenu.item_title.set()

    async with kwargs["state"].proxy() as data:
        data["item_id"]=item_id
        data['action']=action

    item = await db.get_item_info(int(item_id))
    text = f"Редактирование <b>{item[0]['title']}</b>\n\n"
    text += f"Описание\n\n"
    text += f"{item[0]['description']}\n"
    text += f"Цена: {item[0]['price']}\n\n"
    text += "<b>ШАГ [1/4]</b>Введите название блюда"
    await callback.message.edit_text(text=text)


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

    text = "<b>ШАГ [2/4]</b>Введите описание блюда"
    await message.answer(text=text)


### Ловлю описание блюда
@dp.message_handler(content_types=["text"], state=MainMenu.item_desc)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.item_price.set()
    async with state.proxy() as data:
        data['desc'] = message.text

    text = "<b>ШАГ [3/4]</b>Введите цену блюда"
    await message.answer(text=text)


### Ловлю цену блюда
@dp.message_handler(content_types=["text"], state=MainMenu.item_price)
async def edit_menu_item_description(message: types.Message, state: FSMContext):
    await MainMenu.item_photo.set()
    async with state.proxy() as data:
        data['price'] = message.text

    text = "<b>ШАГ [4/4]</b>Загрузите изображение блюда"
    await message.answer(text=text)


### Ловлю изображение блюда
@dp.message_handler(content_types=types.ContentType.PHOTO, state=MainMenu.item_photo)
async def edit_menu_item_description(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id

    await message.photo[-1].download(f'media/{data["photo"]}.jpg')

    text = f"Готово\n\n{data}"

    await message.answer(text=text)
    data = await state.get_data()

    title = data['title']
    description = data['desc']
    price = data['price']
    photo = data['photo']

    if data["action"] == "new_item":
        category_id = data['category_id']
        record_id = await db.add_new_dish(
                                        title=title,
                                        description=description,
                                        price=float(price),
                                        photo=photo,
                                        category_id=category_id
        )

        print("Добавить новое блюдо в БД")
    elif data["action"] == "edit_item":
        item_id = data['item_id']

        await db.edit_dish(title=title, description=description, price=float(price), photo=photo, item_id=item_id)
        print("Изменить текущее блюдо в БД")

    data = await state.get_data()
    await MainMenu.main.set()


### Ловлю нажатие на кнопку удалить блюдо
async def delete_item(callback: types.CallbackQuery, item_id, **kwargs):
    await db.delete_item(id=int(item_id))
