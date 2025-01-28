from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command('start'))
async def start_bot_command(msg: types.Message):
    await msg.answer(f'Hello, {msg.from_user.full_name}')