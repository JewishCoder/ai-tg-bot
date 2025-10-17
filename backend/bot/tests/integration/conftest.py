"""Фикстуры для интеграционных тестов с реальной БД."""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import Config
from src.database import Database
from src.models import Base
from src.storage import Storage


@pytest.fixture
async def test_db_engine() -> AsyncEngine:
    """
    Создаёт in-memory SQLite движок для тестов.

    Returns:
        AsyncEngine для SQLite in-memory
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_database(test_db_engine: AsyncEngine) -> Database:
    """
    Создаёт Database объект для тестов.

    Args:
        test_db_engine: Тестовый движок БД

    Returns:
        Database объект
    """
    # Создаём минимальный config для Database
    test_config = Config(
        telegram_token="test-token",
        openrouter_api_key="test-key",
        openrouter_model="test-model",
        db_password="test-password",
    )

    # Создаём Database и заменяем engine на тестовый
    database = Database(test_config)
    await database.engine.dispose()  # Закрываем дефолтный engine

    # Подменяем на тестовый engine
    database.engine = test_db_engine
    database.session_factory = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return database


@pytest.fixture
async def integration_storage(test_database: Database) -> Storage:
    """
    Создаёт Storage с реальной БД для интеграционных тестов.

    Args:
        test_database: Тестовая БД

    Returns:
        Storage с реальной БД
    """
    test_config = Config(
        telegram_token="test-token",
        openrouter_api_key="test-key",
        openrouter_model="test-model",
        db_password="test-password",
        max_history_messages=50,
        cache_ttl=300,
        cache_max_size=1000,
        max_context_messages=20,
    )

    return Storage(test_database, test_config)
