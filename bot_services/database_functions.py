import asyncio
from datetime import datetime
from bot_services.database_core import get_async_session, UserData, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pytz

# Функция добавления данных пользователя в базу данных
async def insert_new_user_info(user_id: int, username: str | None,
                               full_name: str | None) -> None:
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | id | user_id    | username | full_name | registration_date | admin_rank | home_address   | phone_number |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | 1  | 7120390123 | Marzkv   | Marsik    | 30.01.2025        | 0          | Afrika, Mongoa | 81234567800  |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+

    # Часовой пояс Екатеринбурга (UTC+5)
    ekb_tz = pytz.timezone("Asia/Yekaterinburg")
    now_ekb = datetime.now(ekb_tz)
    registration_date = now_ekb.strftime("%Y-%m-%d %H:%M:%S")
    checking_flag = await update_and_check_user_data(user_id, username, full_name)
    if checking_flag is False:
        async for session in get_async_session():
            users = [
                UserData(
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    registration_date=registration_date,
                    admin_rank=0,
                    phone_number=None,
                    home_address=None
                )
            ]
            session.add_all(users)
            await session.commit()
    else:
        pass

# Функция проверки и обновления пользовательских данных
async def update_and_check_user_data(user_id: int, username: str,
                                     full_name: str) -> bool:
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | id | user_id    | username | full_name | registration_date | admin_rank | home_address   | phone_number |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | 1  | 7120390123 | Marzkv   | Marsik    | 30.01.2025        | 0          | Afrika, Mongoa | 81234567800  |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # username =  mrzkv, full_name = Marsik123 => update_data
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | id | user_id    | username | full_name | registration_date | admin_rank | home_address   | phone_number |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | 1  | 7120390123 | mrzkv   | Marsik123  | 30.01.2025        | 0          | Afrika, Mongoa | 81234567800  |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    async for session in get_async_session():
        result = await session.execute(
            select(UserData).where(UserData.user_id == user_id)
        )
        user_data = result.scalars().first()

        if user_data:
            if user_data.username != username or user_data.full_name != full_name:
                await session.execute(
                    UserData.__table__.update()
                    .where(UserData.user_id == user_id)
                    .values(username=username, full_name=full_name)
                )
                await session.commit()
                return True  # Данные обновлены
            if user_data.username == username and user_data.full_name == full_name:
                return True  # Данные уже актуальны
        else:
            return False  # Пользователь не найден

