from aiogram import Router, types
from aiogram.filters import Command
from bot_services.database_functions import insert_new_user_info

router = Router()

@router.message(Command('start'))
async def start_bot_command(msg: types.Message):
    await insert_new_user_info(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    await msg.answer(f'Hello, {msg.from_user.full_name}')
