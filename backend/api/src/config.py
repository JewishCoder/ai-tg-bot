"""Конфигурация API."""

import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """
    Конфигурация API сервера.

    Загружается из переменных окружения или .env файла.
    """

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_VERSION: str = "v1"

    # StatCollector
    COLLECTOR_MODE: str = Field(default="mock", description="Collector mode: 'mock' or 'real'")

    # Database settings (для collector_mode='real')
    DB_HOST: str = Field(default="localhost", description="PostgreSQL host")
    DB_PORT: int = Field(default=5432, description="PostgreSQL port")
    DB_NAME: str = Field(default="ai_tg_bot", description="Database name")
    DB_USER: str = Field(default="postgres", description="Database user")
    DB_PASSWORD: str = Field(default="postgres", description="Database password")
    DB_POOL_SIZE: int = Field(default=5, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")

    # Cache settings (для Real collector)
    CACHE_TTL: int = Field(default=60, description="Cache TTL in seconds")
    CACHE_MAXSIZE: int = Field(default=100, description="Cache max size")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:8081",  # Nginx reverse proxy
            "http://localhost:3000",  # Frontend direct (dev)
            "http://localhost:5173",  # Vite dev server
        ],
        description="Allowed CORS origins",
    )

    # Logging
    LOG_LEVEL: str = "INFO"

    # Auth settings
    ADMIN_REGISTRATION_TOKEN: str = Field(
        default="change-me-in-production",
        description="Admin token for user registration",
    )

    # Rate limiting
    STATS_API_RATE_LIMIT: str = Field(
        default="10/minute", description="Rate limit for stats endpoint"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        """
        Валидирует CORS origins.

        Предупреждает если используется wildcard "*" (не рекомендуется для production).
        """
        if "*" in v:
            logger.warning(
                "CORS wildcard '*' detected in CORS_ORIGINS. "
                "Not recommended for production! Use specific origins instead."
            )
        return v

    @property
    def database_url(self) -> str:
        """
        Формирует psycopg3 URL для подключения к БД.

        Returns:
            URL в формате postgresql+psycopg://user:password@host:port/dbname
        """
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Глобальный экземпляр конфигурации
config = Config()
