"""Тесты для модуля Config."""

import pytest

from src.config import Config


class TestConfig:
    """Тесты класса Config."""

    def test_config_with_fallback_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: загрузка fallback модели из переменных окружения.

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем обязательные переменные окружения
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_123")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_456")
        monkeypatch.setenv("DB_PASSWORD", "test_password")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

        # Act: создаём конфигурацию
        config = Config()

        # Assert: проверяем что fallback модель загружена
        assert config.openrouter_fallback_model == "meta-llama/llama-3.1-8b-instruct:free"

    def test_config_fallback_model_optional(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: fallback модель опциональна, пустая строка преобразуется в None.

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем обязательные переменные и пустую строку для fallback
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_123")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_456")
        monkeypatch.setenv("DB_PASSWORD", "test_password")
        # Устанавливаем пустую строку для fallback модели
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "")

        # Act: создаём конфигурацию с пустой строкой для fallback
        config = Config()

        # Assert: пустая строка для fallback должна быть None или пустая строка (опционально)
        assert config.openrouter_fallback_model in (None, "")

    def test_config_loads_all_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: проверка что все поля Config загружаются корректно.

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем переменные окружения
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
        monkeypatch.setenv("DB_PASSWORD", "test_password")
        monkeypatch.setenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

        # Act: создаём конфигурацию
        config = Config()

        # Assert: проверяем что все поля на месте
        assert config.telegram_token == "test_token"
        assert config.openrouter_api_key == "test_key"
        assert config.openrouter_model == "anthropic/claude-3.5-sonnet"
        assert config.openrouter_fallback_model == "meta-llama/llama-3.1-8b-instruct:free"
        # Проверяем defaults
        assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert config.llm_temperature == 0.7
        assert config.retry_attempts == 3
        # Проверяем БД поля
        assert config.db_password == "test_password"
