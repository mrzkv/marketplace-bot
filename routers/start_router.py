from aiogram import Router, types
from aiogram.filters import Command
from bot_services.database_functions import insert_new_user_info, check_user_ban_info, get_username_by_user_id
import html
router = Router()

@router.message(Command('start'))
async def start_bot_command(msg: types.Message):
    await insert_new_user_info(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    ban_data = await check_user_ban_info(msg.from_user.id)
    if ban_data:
        admin_data = await get_user_data_by_user_id(ban_data.admin_id)
        text_data = (f'Вы были заблокированы.\n'
                     f'Админ: @{html.escape(admin_username)}\n'
                     f'Причина: {html.escape(ban_data.reason)}\n'
                     f'Дополнительная информация: {html.escape(ban_data.additional_info)}\n'
                     f'Дата блокировки: {html.escape(ban_data.date)}.')

        await msg.answer(text=text_data)
    else:
        await msg.answer(text=f'Hi, {html.escape(msg.from_user.username)}')
