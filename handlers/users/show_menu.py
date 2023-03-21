from data.config import admins
from keyboards.default import menuUser, menuAdmin
from keyboards.inline.inline_show_menu_buttons import menu_cd_show, show_menu_buttons
from aiogram.types import CallbackQuery
from loader import dp, bot

from utils.db_api.db_commands import DBCommands

db = DBCommands()


@dp.callback_query_handler(menu_cd_show.filter())
async def out_categories(call: CallbackQuery, callback_data: dict):
    """Обработчик нажатий на кнопки меню"""
    category_id = callback_data['category_id']
    message_id = callback_data['message_id']

    if (callback_data['exit']) == "Exit":
        await bot.delete_message(chat_id=call.message.chat.id, message_id=message_id)

        if str(call.from_user.id) == admins[0]:
            markup = menuAdmin
        else:
            markup = menuUser

        await call.message.answer(text="Главное меню", reply_markup=markup)
    else:
        markup = await show_menu_buttons(message_id=message_id)

        info = await db.get_category_info(id=int(category_id))

        text = f"""Выбрана категория {info[0]['title']}\n\n
            {info[0]['url']}
        """
        await call.message.edit_text(text=text, reply_markup=markup)
