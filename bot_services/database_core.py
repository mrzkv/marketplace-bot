import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()
async_engine: AsyncEngine = create_async_engine(
        url= f'sqlite+aiosqlite:///app.db',
        echo=True)
Async_Session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)



# Асинхронный генератор сессий
async def get_async_session() -> AsyncSession:
    """
    Для использования пишем это:
    async for session in await get_async_session():
    """
    async with Async_Session() as session:
        yield session

# Таблица пользовательских профилей
class UserProfileData(Base):
    __tablename__ = 'users_profile'
    id = Column(Integer, primary_key=True, autoincrement=True, unique = True)  # Автоинкрементный ID
    user_id = Column(Integer, nullable=False, unique=True)  # ID пользователя, число
    photo = Column(String, nullable= True) # Фото пользователя, телеграм строка
    phone_number = Column(String, nullable=True)  # Номер телефона, строка
    home_address = Column(String, nullable=True)  # Домашний адрес, строка
    surname_name = Column(String, nullable=True) # Фамилия Имя, строка


# Таблица данных пользователей
class UserData(Base):
    __tablename__ = 'users_data'
    id = Column(Integer, primary_key=True, autoincrement=True, unique = True)  # Автоинкрементный ID
    user_id = Column(Integer, nullable=False, unique=True)  # ID пользователя
    username = Column(String, nullable=True)  # Юзернейм, строка
    full_name = Column(String, nullable=True)  # Полное имя, строка
    registration_date = Column(String, nullable=False)  # Дата регистрации
    admin_rank = Column(Integer, nullable=False)  # Ранг администратора, строка

# Таблица заблокированных пользователей
class BlockedUsers(Base):
    __tablename__ = 'blocked_users'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Автоинкрементный ID
    user_id = Column(Integer, nullable=False)  # ID пользователя
    reason = Column(String, nullable=False)  # Причина блокировки
    admin_id = Column(Integer, nullable=False) # ID админа
    additional_info = Column(String, nullable=True) # Дополнительная информация
    date = Column(String, nullable=True)  # Дата блокировки


# Создание базы данных и таблиц
async def create_database_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

