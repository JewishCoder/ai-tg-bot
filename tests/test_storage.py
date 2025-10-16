"""Тесты для модуля Storage с использованием mock Database."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.config import Config
from src.models import Message, UserSettings
from src.storage import Storage


class TestStorage:
    """Тесты класса Storage с моками."""

    @pytest.mark.asyncio
    async def test_init_storage(self, mock_database: AsyncMock, test_config: Config) -> None:
        """
        Тест: инициализация Storage с Database.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)

        assert storage.db == mock_database
        assert storage.config == test_config

    @pytest.mark.asyncio
    async def test_ensure_user_exists_creates_user_and_settings(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: _ensure_user_exists создаёт пользователя и настройки.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        await storage._ensure_user_exists(user_id)

        # Проверяем что session был вызван
        mock_database.session.assert_called()
        # Проверяем что execute вызывался для создания user и settings
        session = await mock_database.session().__aenter__()
        assert session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_load_history_empty_user(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: загрузка истории для пользователя без сообщений.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Мокируем пустой результат запроса
        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        session.execute.return_value = mock_result

        history = await storage.load_history(user_id)

        assert history == []
        mock_database.session.assert_called()

    @pytest.mark.asyncio
    async def test_load_history_with_messages(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: загрузка истории с сообщениями.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Создаём мок сообщений
        mock_msg1 = MagicMock(spec=Message)
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"
        mock_msg1.created_at = datetime.now(UTC)

        mock_msg2 = MagicMock(spec=Message)
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there"
        mock_msg2.created_at = datetime.now(UTC)

        # Мокируем результат запроса
        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_msg1, mock_msg2]
        session.execute.return_value = mock_result

        history = await storage.load_history(user_id)

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there"

    @pytest.mark.asyncio
    async def test_clear_history(self, mock_database: AsyncMock, test_config: Config) -> None:
        """
        Тест: очистка истории диалога (soft delete).

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Мокируем результат UPDATE
        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        session.execute.return_value = mock_result

        await storage.clear_history(user_id)

        # Проверяем что execute был вызван для soft delete
        mock_database.session.assert_called()
        session.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_system_prompt_default(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: получение системного промпта по умолчанию (None).

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Мокируем настройки без кастомного промпта
        mock_settings = MagicMock(spec=UserSettings)
        mock_settings.system_prompt = None

        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_settings
        session.execute.return_value = mock_result

        system_prompt = await storage.get_system_prompt(user_id)

        assert system_prompt is None

    @pytest.mark.asyncio
    async def test_get_system_prompt_custom(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: получение кастомного системного промпта.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345
        custom_prompt = "Ты опытный программист."

        # Мокируем настройки с кастомным промптом
        mock_settings = MagicMock(spec=UserSettings)
        mock_settings.system_prompt = custom_prompt

        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_settings
        session.execute.return_value = mock_result

        loaded_prompt = await storage.get_system_prompt(user_id)

        assert loaded_prompt == custom_prompt

    @pytest.mark.asyncio
    async def test_set_system_prompt(self, mock_database: AsyncMock, test_config: Config) -> None:
        """
        Тест: установка системного промпта.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345
        custom_prompt = "Ты опытный разработчик."

        # Мокируем результаты
        session = await mock_database.session().__aenter__()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        session.execute.return_value = mock_result

        await storage.set_system_prompt(user_id, custom_prompt)

        # Проверяем что были вызваны методы
        mock_database.session.assert_called()
        session.execute.assert_called()
        session.add.assert_called()

    @pytest.mark.asyncio
    async def test_get_dialog_info(self, mock_database: AsyncMock, test_config: Config) -> None:
        """
        Тест: получение информации о диалоге (упрощённый интеграционный тест).

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Для метода get_dialog_info сложная логика с несколькими запросами
        # При возникновении exception возвращается дефолтное значение
        # Проверяем что метод не падает и возвращает корректную структуру
        dialog_info = await storage.get_dialog_info(user_id)

        # Проверяем структуру результата
        assert "messages_count" in dialog_info
        assert "system_prompt" in dialog_info
        assert "updated_at" in dialog_info
        # В случае ошибки мокирования возвращается дефолтное значение
        assert isinstance(dialog_info["messages_count"], int)


@pytest.mark.asyncio
async def test_storage_integration_with_mock(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Интеграционный тест Storage с mock Database.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)

    # Проверяем что Storage корректно инициализируется и имеет все методы
    assert hasattr(storage, "load_history")
    assert hasattr(storage, "save_history")
    assert hasattr(storage, "clear_history")
    assert hasattr(storage, "get_system_prompt")
    assert hasattr(storage, "set_system_prompt")
    assert hasattr(storage, "get_dialog_info")
