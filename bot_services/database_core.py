import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

Base = declarative_base()
async_engine = create_async_engine(
        url= 'sqlite+aiosqlite:///app.db',
        echo=True)


# Таблица данных пользователей
class UserData(Base):
    __tablename__ = 'users_data'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Автоинкрементный ID
    user_id = Column(Integer, nullable=False)  # Число, не нулевое
    username = Column(String, nullable=True)  # Строка
    full_name = Column(String, nullable=True)  # Полное имя, строка
    registration_date = Column(String, nullable=False)  # Дата регистрации
    admin_rank = Column(String, nullable=False)  # Ранг администратора, строка
    phone_number = Column(String, nullable=True)  # Номер телефона, строка
    home_address = Column(String, nullable=True)  # Домашний адрес, строка

# Таблица заблокированных пользователей
class BlockedUsers(Base):
    __tablename__ = 'blocked_users'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Автоинкрементный ID
    user_id = Column(Integer, nullable=False)  # Число, не нулевое
    reason = Column(String, nullable=False)  # Причина блокировки
    admin_username = Column(String, nullable=False) # Юзернейм админа
    additional_info = Column(String, nullable=True) # Дополнительная информация
    date = Column(String, nullable=True)  # Дата блокировки


# Создание базы данных и таблиц
async def create_database_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


