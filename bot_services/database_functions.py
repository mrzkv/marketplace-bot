import asyncio
from datetime import datetime
from bot_services.database_core import get_async_session, UserData, Base, BlockedUsers, UserProfileData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pytz
import html

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
    registration_date = now_ekb.strftime("%Y.%m.%d %H:%M:%S")
    await insert_new_user_profile_info(user_id)
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
                )
            ]
            session.add_all(users)
            await session.commit()
    else:
        pass

# Создает строку в таблице пользовательских профилей
async def insert_new_user_profile_info(user_id: int) -> None:
    async for session in get_async_session():
        result = await session.execute(
            select(UserProfileData).where(UserProfileData.user_id == user_id)
        )
        if result.scalar() is not None:
            checking_flag = False
        else:
            checking_flag = True
        await session.close()
    if checking_flag is False:
        return None
    async for session in get_async_session():
        users = [
            UserProfileData(
                user_id=user_id,
                photo='',
                phone_number='',
                home_address='',
                surname_name=''
            )
        ]
        session.add_all(users)
        await session.commit()

# Функция проверки и обновления пользовательских данных
async def update_and_check_user_data(user_id: int, username: str,
                                     full_name: str) -> bool:
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # | id | user_id    | username | full_name | registration_date | admin_rank | home_address   | phone_number |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # |  1 | 7120390123 | Marzkv   | Marsik    | 30.01.2025        | 0          | Afrika, Mongoa | 81234567800  |
    # +----+------------+----------+-----------+-------------------+------------+----------------+--------------+
    # username =  mrzkv, full_name = Marsik123 => update_data
    # +----+------------+----------+-----------+---------------------+------------+----------------+--------------+
    # | id | user_id    | username | full_name |  registration_date  | admin_rank | home_address   | phone_number |
    # +----+------------+----------+-----------+---------------------+------------+----------------+--------------+
    # |  1 | 7120390123 | mrzkv   | Marsik123  | 30.01.2025 14:14:14 |      0     | Afrika, Mongoa | 81234567800  |
    # +----+------------+----------+-----------+---------------------+------------+----------------+--------------+
    async for session in get_async_session():
        result = await session.execute(
            select(UserData).where(UserData.user_id == user_id)
        )
        user_data = result.scalar()

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


# Проверка пользователя на блокировку
async def check_user_ban_info(user_id: int) -> str | None:
    # +----+------------+-----------------+----------------+------------------------+-------------------+
    # | id |   user_id  |     reason      | admin_username |    additional_info     |        date       |
    # +----+------------+-----------------+----------------+------------------------+-------------------+
    # | 1  | 7120390123 | Lying to admins |     mrzkv      | Закинь сотку за разбан | 30.01.25 21:58:11 |
    # +----+------------+-----------------+----------------+------------------------+-------------------+
    async for session in get_async_session():
        result = await session.execute(
            select(BlockedUsers).where(BlockedUsers.user_id == user_id)
        )
        ban_data = result.scalar()
        await session.close()
        if ban_data:  # Если пришло не None, то выводится
            admin_data = await get_user_data_by_user_id(ban_data.admin_id)
            text_data = (f'Вы были заблокированы.\n'
                         f'Админ: @{html.escape(admin_data.username)}\n'
                         f'Причина: {html.escape(ban_data.reason)}\n'
                         f'Дополнительная информация: {html.escape(ban_data.additional_info)}\n'
                         f'Дата блокировки: {html.escape(ban_data.date)}.')
            return text_data
        return None

# Получение данных о пользователе по user_id
async def get_user_data_by_user_id(user_id: int) -> str | None:
    async for session in get_async_session():
        result = await session.execute(
            select(UserData).where(UserData.user_id == user_id)
        )
        user_data = result.scalar()
        await session.close()
        return user_data

# Получение данных о пользовательском профиле по user_id
async def get_user_profile_data(user_id: int) -> str | None:
    async for session in get_async_session():
        result = await session.execute(
            select(UserProfileData).where(UserProfileData.user_id == user_id)
        )
        profile_data = result.scalar()
        await session.close()
        return profile_data

async def insert_profile_data(user_id: int, data: str, type_of_data: str):
    async for session in get_async_session():
        if type_of_data == 'photo_data':
            await session.execute(
                UserProfileData.__table__.update()
                .where(UserProfileData.user_id == user_id)
                .values(photo=data))
        if type_of_data == 'name_surname':
            await session.execute(
                UserProfileData.__table__.update()
                .where(UserProfileData.user_id == user_id)
                .values(surname_name=data))
        if type_of_data == 'phone_number':
            await session.execute(
                UserProfileData.__table__.update()
                .where(UserProfileData.user_id == user_id)
                .values(phone_number=data))
        if type_of_data == 'home_address':
            await session.execute(
                UserProfileData.__table__.update()
                .where(UserProfileData.user_id == user_id)
                .values(home_address=data))
        await session.commit()

#class UserProfileData(Base):
    # __tablename__ = 'users_profile'
    # id = Column(Integer, primary_key=True, autoincrement=True, unique = True)  # Автоинкрементный ID
    # user_id = Column(Integer, nullable=False, unique=True)  # ID пользователя, число
    # photo = Column(String, nullable= True) # Фото пользователя, телеграм строка
    # phone_number = Column(String, nullable=True)  # Номер телефона, строка
    # home_address = Column(String, nullable=True)  # Домашний адрес, строка
    # surname_name = Column(String, nullable=True) # Фамилия Имя, строка
