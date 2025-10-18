"""Управление подключением к базе данных PostgreSQL."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


class Database:
    """
    Класс для управления подключением к базе данных бота.

    Отвечает за:
    - Создание async engine для PostgreSQL
    - Создание session factory для работы с БД
    - Управление connection pooling
    """

    def __init__(self, database_url: str, pool_size: int = 5, max_overflow: int = 10) -> None:
        """
        Инициализация Database с параметрами подключения.

        Args:
            database_url: URL подключения к PostgreSQL (psycopg3)
            pool_size: Размер пула соединений (default: 5)
            max_overflow: Максимальное количество дополнительных соединений (default: 10)
        """
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Не логируем SQL запросы (production)
            pool_pre_ping=True,  # Проверка соединения перед использованием
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Не обновлять объекты после коммита
        )

        logger.info(f"Database initialized: pool_size={pool_size}, max_overflow={max_overflow}")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager для работы с сессией БД.

        Автоматически управляет транзакциями:
        - Commit при успешном выполнении
        - Rollback при ошибках

        Yields:
            AsyncSession для выполнения запросов к БД

        Example:
            async with database.session() as session:
                result = await session.execute(select(User))
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """
        Закрывает все соединения с базой данных.

        Должен вызываться при остановке приложения.
        """
        await self.engine.dispose()
        logger.info("Database connections closed")
