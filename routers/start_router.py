from aiogram import Router, types, F
from aiogram.filters import Command
from bot_services.database_functions import insert_new_user_info, check_user_ban_info, get_user_data_by_user_id
import html
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
router = Router()


# Обработка /start
@router.message(Command('start'))
async def start_bot_command(data: types.Message) -> None:
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    kb = [[types.InlineKeyboardButton(text='Ваш профиль', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await data.answer(text=f'Вы в меню', reply_markup=keyboard)