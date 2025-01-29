from asyncio import run
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot_services.database_core import create_database_and_tables
from routers.start_router import router as start_router
from bot_services.config import get_token

dp = Dispatcher()
dp.include_router(start_router)


async def main():
    await create_database_and_tables()
    token_of_bot = await get_token()
    bot = Bot(token=token_of_bot, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # API бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    run( main() )