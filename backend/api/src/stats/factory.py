"""Factory для создания StatCollector на основе конфигурации."""

import logging

from src.config import Config
from src.database import Database

from .collector import StatCollector
from .mock_collector import MockStatCollector
from .real_collector import RealStatCollector

logger = logging.getLogger(__name__)


def create_stat_collector(config: Config) -> StatCollector:
    """
    Фабрика для создания StatCollector.

    Args:
        config: Конфигурация приложения

    Returns:
        MockStatCollector или RealStatCollector в зависимости от config.COLLECTOR_MODE

    Raises:
        ValueError: Если COLLECTOR_MODE невалиден
    """
    mode = config.COLLECTOR_MODE.lower()

    if mode == "mock":
        logger.info("Creating MockStatCollector (test data generator)")
        return MockStatCollector(seed=42)

    if mode == "real":
        logger.info("Creating RealStatCollector (PostgreSQL backend)")
        database = Database(
            database_url=config.database_url,
            pool_size=config.DB_POOL_SIZE,
            max_overflow=config.DB_MAX_OVERFLOW,
        )
        return RealStatCollector(
            database=database,
            cache_ttl=config.CACHE_TTL,
            cache_maxsize=config.CACHE_MAXSIZE,
        )

    raise ValueError(
        f"Invalid COLLECTOR_MODE: {mode}. Must be 'mock' or 'real'. "
        f"Set COLLECTOR_MODE environment variable."
    )
