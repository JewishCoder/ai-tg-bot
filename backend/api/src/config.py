"""Конфигурация API."""

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    STAT_COLLECTOR_TYPE: str = "mock"  # mock или real

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Глобальный экземпляр конфигурации
config = Config()
