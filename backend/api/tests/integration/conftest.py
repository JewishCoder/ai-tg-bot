"""Fixtures для integration тестов.

Integration тесты используют PostgreSQL, так как RealStatCollector
использует PostgreSQL-специфичные SQL функции (date_trunc, EXTRACT).
"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import Config
from src.database import Database
from src.models import Base, Message, User, UserSettings

# Windows fix: psycopg требует SelectorEventLoop вместо ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Создаёт PostgreSQL движок для integration тестов.

    Использует переменные окружения для подключения к тестовой БД.

    Yields:
        AsyncEngine для PostgreSQL
    """
    db_host = os.getenv("TEST_DB_HOST", "localhost")
    db_port = os.getenv("TEST_DB_PORT", "5432")
    db_name = os.getenv("TEST_DB_NAME", "ai_tg_bot")
    db_user = os.getenv("TEST_DB_USER", "botuser")
    db_password = os.getenv("TEST_DB_PASSWORD", "botpass")

    engine = create_async_engine(
        f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    # Создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Cleanup перед тестами: удаляем тестовые данные (user_id >= 900000)
    async with engine.begin() as conn:
        await conn.execute(delete(Message).where(Message.user_id >= 900000))
        await conn.execute(delete(UserSettings).where(UserSettings.user_id >= 900000))
        await conn.execute(delete(User).where(User.id >= 900000))
        await conn.commit()

    yield engine

    # Cleanup после тестов: удаляем тестовые данные (user_id >= 900000)
    async with engine.begin() as conn:
        await conn.execute(delete(Message).where(Message.user_id >= 900000))
        await conn.execute(delete(UserSettings).where(UserSettings.user_id >= 900000))
        await conn.execute(delete(User).where(User.id >= 900000))
        await conn.commit()

    await engine.dispose()


@pytest.fixture
async def integration_database(test_db_engine: AsyncEngine) -> Database:
    """
    Создаёт Database объект для тестов с подменой engine.

    Args:
        test_db_engine: Тестовый движок БД (SQLite или PostgreSQL)

    Returns:
        Database объект для тестов
    """
    # Создаём минимальный config
    test_config = Config(
        COLLECTOR_MODE="real",
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_password",
        DB_POOL_SIZE=5,
        DB_MAX_OVERFLOW=10,
        CACHE_TTL=1,  # Короткий TTL для тестов
        CACHE_MAXSIZE=10,
    )

    # Создаём Database
    database = Database(
        database_url=test_config.database_url,
        pool_size=test_config.DB_POOL_SIZE,
        max_overflow=test_config.DB_MAX_OVERFLOW,
    )

    # Закрываем дефолтный engine
    await database.engine.dispose()

    # Подменяем на тестовый engine
    database.engine = test_db_engine
    database.session_factory = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return database
