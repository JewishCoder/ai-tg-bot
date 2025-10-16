"""Конфигурация приложения."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Конфигурация приложения.

    Загружается из переменных окружения или .env файла (если указан).
    Переменные окружения имеют приоритет над .env файлом.

    Обязательные параметры: telegram_token, openrouter_api_key.
    """

    # Telegram Bot
    telegram_token: str = Field(..., description="Telegram Bot API token")

    # OpenRouter LLM
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", description="OpenRouter API base URL"
    )
    openrouter_model: str = Field(
        default="anthropic/claude-3.5-sonnet", description="LLM model to use"
    )
    openrouter_fallback_model: str | None = Field(
        default=None, description="Fallback LLM model to use when primary model fails"
    )

    # System Prompt
    system_prompt: str = Field(
        default="Ты полезный ассистент. Отвечай на вопросы пользователей четко и по делу.",
        description="Default system prompt for LLM",
    )

    # LLM Parameters
    llm_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature (0.0 - 2.0)"
    )
    llm_max_tokens: int = Field(default=1000, gt=0, description="Maximum tokens in LLM response")
    max_history_messages: int = Field(
        default=50, gt=0, description="Maximum number of messages to keep in history"
    )

    # Retry Configuration
    retry_attempts: int = Field(
        default=3, ge=1, description="Number of retry attempts for LLM API calls"
    )
    retry_delay: float = Field(
        default=1.0, ge=0.1, description="Delay between retry attempts in seconds"
    )

    # Directories
    data_dir: str = Field(default="data", description="Directory for storing dialog history files")
    logs_dir: str = Field(default="logs", description="Directory for storing log files")

    # Database
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="ai_tg_bot", description="Database name")
    db_user: str = Field(default="botuser", description="Database user")
    db_password: str = Field(..., description="Database password")
    db_echo: bool = Field(default=False, description="SQLAlchemy echo for debugging")

    # Logging
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    @property
    def database_url(self) -> str:
        """
        Формирует URL для подключения к базе данных.

        Returns:
            URL строка для asyncpg драйвера PostgreSQL
        """
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
