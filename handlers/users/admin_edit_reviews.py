from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from keyboards.default import cancel_btn, menuAdmin

from loader import dp, bot
from utils.db_api.db_commands import DBCommands

db = DBCommands()


@dp.message_handler(Text(contains=["Редактировать отзывы"]), state='*')
async def edit_reviews(message: types.Message, state: FSMContext):
    """Ловлю нажатие на кнопку Редактировать отзывы"""
    data = await state.get_data()
    id_msg_list = data['id_msg_list']

    try:
        reviews = await db.get_approved_reviews()
    except Exception as _ex:
        return

    await message.answer(text="Последние 15 отзывов")

    for item in reviews[-15:]:
        text = f"Отзыв оставил @{item['username']}\n"
        text += f"{item['text']}"

        msg = await message.answer(
            text=text,
            reply_markup=
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"Удалить", callback_data=f"edit_review-{str(item['id'])}")]
                ]
            )
        )
        id_msg_list.append(msg.message_id)

    async with state.proxy() as data:
        data['id_msg_list'] = id_msg_list


@dp.callback_query_handler(text_contains="edit_review", state="*")
async def delete_review(call: types.CallbackQuery, state: FSMContext):
    """Удаление отзыва с доски"""
    data = call.data.split("-")
    await call.answer()
    await db.deactivate_review(id=data[-1])
    await call.message.answer(text="Отзыв успешно удален")
