"""Управление подключением к базе данных."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import Config

logger = logging.getLogger(__name__)


class Database:
    """
    Класс для управления подключением к базе данных.

    Отвечает за:
    - Создание async engine для PostgreSQL
    - Создание session factory для работы с БД
    - Управление жизненным циклом подключений
    """

    def __init__(self, config: Config) -> None:
        """
        Инициализация Database с конфигурацией.

        Args:
            config: Конфигурация приложения с параметрами БД
        """
        self.config = config
        self.engine = create_async_engine(
            config.database_url,
            echo=config.db_echo,
            pool_pre_ping=True,  # Проверка соединения перед использованием
            pool_size=5,  # Размер пула соединений
            max_overflow=10,  # Максимальное количество дополнительных соединений
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Не обновлять объекты после коммита
        )

        logger.info(
            f"Database initialized: host={config.db_host}, "
            f"port={config.db_port}, db={config.db_name}"
        )

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
