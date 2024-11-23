from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/cargo_db")

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Сессия для асинхронных операций
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()

# Асинхронный контекстный менеджер для работы с сессиями
async def get_db():
    async with SessionLocal() as db:
        yield db


# Функция для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
