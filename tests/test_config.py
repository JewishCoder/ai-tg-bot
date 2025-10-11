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
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

        # Act: создаём конфигурацию
        config = Config()

        # Assert: проверяем что fallback модель загружена
        assert config.openrouter_fallback_model == "meta-llama/llama-3.1-8b-instruct:free"

    def test_config_fallback_model_optional(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: fallback модель опциональна (default=None).

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем только обязательные переменные
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_123")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_456")
        # НЕ устанавливаем OPENROUTER_FALLBACK_MODEL

        # Act: создаём конфигурацию без fallback модели
        config = Config()

        # Assert: fallback модель должна быть None (опциональна)
        assert config.openrouter_fallback_model is None

    def test_config_fallback_model_empty_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: пустая строка для fallback модели обрабатывается как None.

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем fallback модель как пустую строку
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_123")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_456")
        monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "")

        # Act: создаём конфигурацию
        config = Config()

        # Assert: пустая строка трактуется как None
        assert config.openrouter_fallback_model is None or config.openrouter_fallback_model == ""

    def test_config_loads_all_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Тест: проверка что все поля Config загружаются корректно.

        Args:
            monkeypatch: Fixture для изменения переменных окружения
        """
        # Arrange: устанавливаем переменные окружения
        monkeypatch.setenv("TELEGRAM_TOKEN", "test_token")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
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
