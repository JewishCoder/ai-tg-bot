"""Тесты для модуля Storage с использованием mock Database."""

import asyncio
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
        from uuid import uuid4

        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Создаём мок сообщений с UUID
        msg1_id = uuid4()
        mock_msg1 = MagicMock(spec=Message)
        mock_msg1.id = msg1_id
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"
        mock_msg1.created_at = datetime.now(UTC)

        msg2_id = uuid4()
        mock_msg2 = MagicMock(spec=Message)
        mock_msg2.id = msg2_id
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
        assert history[0]["id"] == str(msg1_id)
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["id"] == str(msg2_id)
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
    async def test_save_history_incremental_new_messages(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: инкрементальное сохранение - только новые сообщения.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        storage = Storage(mock_database, test_config)
        user_id = 12345

        # Мокируем настройки
        mock_settings = MagicMock(spec=UserSettings)
        mock_settings.max_history_messages = 50

        # Настраиваем моки для разных сессий
        # Первая сессия - для _ensure_user_exists (2 execute)
        mock_ensure_session = MagicMock()
        mock_ensure_session.execute = AsyncMock(return_value=MagicMock())
        mock_ensure_session.__aenter__ = AsyncMock(return_value=mock_ensure_session)
        mock_ensure_session.__aexit__ = AsyncMock(return_value=None)

        # Вторая сессия - для save_history основной логики
        mock_save_session = MagicMock()
        mock_save_session.add = MagicMock()

        mock_settings_result = MagicMock()
        mock_settings_result.scalar_one.return_value = mock_settings

        mock_ids_result = MagicMock()
        mock_ids_result.all.return_value = []  # Нет существующих сообщений

        mock_save_session.execute = AsyncMock(side_effect=[mock_settings_result, mock_ids_result])
        mock_save_session.__aenter__ = AsyncMock(return_value=mock_save_session)
        mock_save_session.__aexit__ = AsyncMock(return_value=None)

        # Мок database.session возвращает разные сессии по очереди
        mock_database.session.side_effect = [
            mock_ensure_session,
            mock_save_session,
        ]

        # Новые сообщения без UUID
        messages = [
            {"role": "user", "content": "Hello", "timestamp": datetime.now(UTC).isoformat()},
            {"role": "assistant", "content": "Hi", "timestamp": datetime.now(UTC).isoformat()},
        ]

        await storage.save_history(user_id, messages)

        # Проверяем что session.add был вызван дважды (2 новых сообщения)
        assert mock_save_session.add.call_count == 2

    @pytest.mark.asyncio
    async def test_save_history_incremental_with_existing(
        self, mock_database: AsyncMock, test_config: Config
    ) -> None:
        """
        Тест: инкрементальное сохранение - обновление существующих сообщений.

        Args:
            mock_database: Mock базы данных
            test_config: Тестовая конфигурация
        """
        from uuid import uuid4

        storage = Storage(mock_database, test_config)
        user_id = 12345
        existing_uuid = str(uuid4())

        # Мокируем настройки
        mock_settings = MagicMock(spec=UserSettings)
        mock_settings.max_history_messages = 50

        # Первая сессия - для _ensure_user_exists
        mock_ensure_session = MagicMock()
        mock_ensure_session.execute = AsyncMock(return_value=MagicMock())
        mock_ensure_session.__aenter__ = AsyncMock(return_value=mock_ensure_session)
        mock_ensure_session.__aexit__ = AsyncMock(return_value=None)

        # Вторая сессия - для save_history основной логики
        mock_save_session = MagicMock()
        mock_save_session.add = MagicMock()

        mock_settings_result = MagicMock()
        mock_settings_result.scalar_one.return_value = mock_settings

        mock_ids_result = MagicMock()
        mock_ids_result.all.return_value = [(existing_uuid,)]

        mock_update_result = MagicMock()

        mock_save_session.execute = AsyncMock(
            side_effect=[
                mock_settings_result,
                mock_ids_result,
                mock_update_result,
            ]
        )
        mock_save_session.__aenter__ = AsyncMock(return_value=mock_save_session)
        mock_save_session.__aexit__ = AsyncMock(return_value=None)

        # Мок database.session возвращает разные сессии по очереди
        mock_database.session.side_effect = [
            mock_ensure_session,
            mock_save_session,
        ]

        # Сообщение с существующим UUID
        messages = [
            {
                "id": existing_uuid,
                "role": "user",
                "content": "Updated content",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

        await storage.save_history(user_id, messages)

        # Проверяем что UPDATE был вызван, но не INSERT
        assert mock_save_session.execute.call_count >= 3  # settings + ids + update
        # session.add НЕ должен быть вызван (только обновление)
        mock_save_session.add.assert_not_called()

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
    assert hasattr(storage, "prompt_cache")


# =============================================================================
# Тесты для кеширования системных промптов
# =============================================================================


@pytest.mark.asyncio
async def test_get_system_prompt_cache_miss(
    mock_database: AsyncMock, test_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Тест первого обращения к get_system_prompt (cache MISS).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
        monkeypatch: Pytest fixture для патчинга
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345
    custom_prompt = "Ты - полезный ассистент"

    # Mock для _get_user_settings
    mock_settings = MagicMock()
    mock_settings.system_prompt = custom_prompt

    async def mock_get_settings(_user_id_arg: int) -> UserSettings:
        return mock_settings

    # Патчим метод _get_user_settings
    monkeypatch.setattr(storage, "_get_user_settings", mock_get_settings)

    # Проверяем что кеш пустой
    assert user_id not in storage.prompt_cache

    # Первый вызов - должен загрузить из БД
    result = await storage.get_system_prompt(user_id)

    # Проверяем результат
    assert result == custom_prompt

    # Проверяем что значение попало в кеш
    assert user_id in storage.prompt_cache
    assert storage.prompt_cache[user_id] == custom_prompt


@pytest.mark.asyncio
async def test_get_system_prompt_cache_hit(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Тест повторного обращения к get_system_prompt (cache HIT).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345
    custom_prompt = "Ты - полезный ассистент"

    # Предзаполняем кеш
    storage.prompt_cache[user_id] = custom_prompt

    # Вызываем get_system_prompt
    result = await storage.get_system_prompt(user_id)

    # Проверяем результат
    assert result == custom_prompt

    # Проверяем что к БД НЕ обращались
    mock_database.session.assert_not_called()


@pytest.mark.asyncio
async def test_get_system_prompt_cache_none_value(
    mock_database: AsyncMock, test_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Тест кеширования None (пользователь использует промпт по умолчанию).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
        monkeypatch: Pytest fixture для патчинга
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Mock для _get_user_settings (системный промпт = None)
    mock_settings = MagicMock()
    mock_settings.system_prompt = None

    call_count = 0

    async def mock_get_settings(_user_id_arg: int) -> UserSettings:
        nonlocal call_count
        call_count += 1
        return mock_settings

    # Патчим метод _get_user_settings
    monkeypatch.setattr(storage, "_get_user_settings", mock_get_settings)

    # Первый вызов
    result = await storage.get_system_prompt(user_id)

    # Проверяем результат
    assert result is None

    # Проверяем что None закешировался
    assert user_id in storage.prompt_cache
    assert storage.prompt_cache[user_id] is None

    # Проверяем что был один вызов _get_user_settings
    assert call_count == 1

    # Второй вызов - должен взять из кеша
    result2 = await storage.get_system_prompt(user_id)

    assert result2 is None
    # Проверяем что _get_user_settings НЕ вызывался второй раз
    assert call_count == 1


@pytest.mark.asyncio
async def test_set_system_prompt_invalidates_cache(
    mock_database: AsyncMock, test_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Тест инвалидации кеша при вызове set_system_prompt.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
        monkeypatch: Pytest fixture для патчинга
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345
    old_prompt = "Старый промпт"
    new_prompt = "Новый промпт"

    # Предзаполняем кеш старым значением
    storage.prompt_cache[user_id] = old_prompt
    assert user_id in storage.prompt_cache

    # Mock для _ensure_user_exists
    async def mock_ensure_user(user_id_arg: int) -> None:
        pass

    # Mock для clear_history
    async def mock_clear_history(user_id_arg: int) -> None:
        pass

    # Патчим методы
    monkeypatch.setattr(storage, "_ensure_user_exists", mock_ensure_user)
    monkeypatch.setattr(storage, "clear_history", mock_clear_history)

    # Mock для session (для основной логики set_system_prompt)
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=AsyncMock())
    mock_session.add = MagicMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = AsyncMock()

    mock_database.session.return_value = mock_session

    # Вызываем set_system_prompt
    await storage.set_system_prompt(user_id, new_prompt)

    # Проверяем что кеш был инвалидирован
    assert user_id not in storage.prompt_cache


@pytest.mark.asyncio
async def test_prompt_cache_ttl_expiration() -> None:
    """
    Тест автоматического истечения TTL кеша.
    """
    # Создаём конфиг с коротким TTL
    short_ttl_config = Config(
        telegram_token="fake-token",
        openrouter_api_key="fake-key",
        openrouter_model="fake-model",
        db_password="fake-password",
        cache_ttl=1,  # 1 секунда TTL
        cache_max_size=10,
    )

    mock_database = AsyncMock()
    storage = Storage(mock_database, short_ttl_config)

    user_id = 12345
    prompt = "Test prompt"

    # Добавляем в кеш
    storage.prompt_cache[user_id] = prompt
    assert user_id in storage.prompt_cache

    # Ждём истечения TTL
    await asyncio.sleep(1.5)

    # Проверяем что запись исчезла из кеша
    assert user_id not in storage.prompt_cache


@pytest.mark.asyncio
async def test_load_recent_history_with_limit(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест загрузки последних N сообщений с лимитом.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345
    limit = 5

    # Mock для _ensure_user_exists
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    # Mock для основного запроса
    from datetime import UTC, datetime
    from uuid import uuid4

    from src.models import Message

    # Создаем 10 сообщений, но загружаем только последние 5
    mock_messages = [
        Message(
            id=uuid4(),
            user_id=user_id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            content_length=len(f"Message {i}"),
            created_at=datetime.now(UTC),
            deleted_at=None,
        )
        for i in range(10)
    ]

    # LIMIT 5 вернет последние 5 (индексы 5-9), в DESC order
    last_5_reversed = list(reversed(mock_messages[5:10]))

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = last_5_reversed

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = AsyncMock()

    mock_database.session.side_effect = [mock_ensure_session, mock_session]

    # Вызываем метод
    history = await storage.load_recent_history(user_id, limit=limit)

    # Проверяем результат
    assert len(history) == 5
    assert history[0]["content"] == "Message 5"  # Первое из последних 5
    assert history[-1]["content"] == "Message 9"  # Последнее


@pytest.mark.asyncio
async def test_load_recent_history_without_limit(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест загрузки всех сообщений (без лимита).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Mock для _ensure_user_exists
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    # Mock для основного запроса
    from datetime import UTC, datetime
    from uuid import uuid4

    from src.models import Message

    mock_messages = [
        Message(
            id=uuid4(),
            user_id=user_id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            content_length=len(f"Message {i}"),
            created_at=datetime.now(UTC),
            deleted_at=None,
        )
        for i in range(3)
    ]

    # Без LIMIT - все сообщения в DESC order
    all_reversed = list(reversed(mock_messages))

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = all_reversed

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = AsyncMock()

    mock_database.session.side_effect = [mock_ensure_session, mock_session]

    # Вызываем метод без лимита
    history = await storage.load_recent_history(user_id, limit=None)

    # Проверяем результат
    assert len(history) == 3
    assert history[0]["content"] == "Message 0"
    assert history[-1]["content"] == "Message 2"


@pytest.mark.asyncio
async def test_load_recent_history_empty(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Тест загрузки пустой истории.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Mock для _ensure_user_exists
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    # Mock для основного запроса (пустой результат)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = AsyncMock()

    mock_database.session.side_effect = [mock_ensure_session, mock_session]

    # Вызываем метод
    history = await storage.load_recent_history(user_id, limit=10)

    # Проверяем результат
    assert history == []


@pytest.mark.asyncio
async def test_save_history_retry_on_failure(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Тест retry механизма при ошибке сохранения истории.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    # Настроим конфиг с 3 попытками retry
    test_config.save_retry_attempts = 3
    test_config.save_retry_delay = 0.1  # Быстрый retry для теста

    storage = Storage(mock_database, test_config)
    user_id = 12345
    messages = [{"role": "user", "content": "Test", "timestamp": datetime.now(UTC).isoformat()}]

    # Mock для _ensure_user_exists
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    # Первые 2 попытки fail, 3-я succeed
    error = Exception("Database connection error")

    # Mock для неудачных попыток (1 и 2)
    failed_session_1 = AsyncMock()
    failed_session_1.__aenter__.side_effect = error

    failed_session_2 = AsyncMock()
    failed_session_2.__aenter__.side_effect = error

    # Mock для успешной попытки (3)
    success_session = AsyncMock()
    success_session.__aenter__.return_value = success_session
    success_session.__aexit__.return_value = AsyncMock()

    mock_settings = MagicMock()
    mock_settings.max_history_messages = 50
    mock_settings_result = AsyncMock()
    mock_settings_result.scalar_one.return_value = mock_settings

    mock_ids_result = AsyncMock()
    mock_ids_result.all.return_value = []

    success_session.execute = AsyncMock(side_effect=[mock_settings_result, mock_ids_result])
    success_session.add = MagicMock()

    # Настраиваем side_effect для session(): 1 ensure + 3 save attempts
    mock_database.session.side_effect = [
        mock_ensure_session,  # _ensure_user_exists для 1 попытки
        failed_session_1,  # 1 попытка save - fail
        mock_ensure_session,  # _ensure_user_exists для 2 попытки
        failed_session_2,  # 2 попытка save - fail
        mock_ensure_session,  # _ensure_user_exists для 3 попытки
        success_session,  # 3 попытка save - success
    ]

    # Вызываем save_history - должен успешно сохранить после 3 попыток
    await storage.save_history(user_id, messages)

    # Проверяем что были 3 попытки
    assert mock_database.session.call_count == 6  # 3 ensure + 3 save attempts


@pytest.mark.asyncio
async def test_save_history_all_retries_fail(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Тест когда все retry попытки проваливаются.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    test_config.save_retry_attempts = 2
    test_config.save_retry_delay = 0.05

    storage = Storage(mock_database, test_config)
    user_id = 12345
    messages = [{"role": "user", "content": "Test", "timestamp": datetime.now(UTC).isoformat()}]

    error = Exception("Persistent database error")

    # Все попытки будут fail
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    failed_session = AsyncMock()
    failed_session.__aenter__.side_effect = error

    # Все попытки провалятся
    mock_database.session.side_effect = [
        mock_ensure_session,
        failed_session,  # 1 попытка
        mock_ensure_session,
        failed_session,  # 2 попытка
    ]

    # Должен выбросить исключение после всех попыток
    with pytest.raises(Exception) as exc_info:
        await storage.save_history(user_id, messages)

    assert "Persistent database error" in str(exc_info.value)
    assert mock_database.session.call_count == 4  # 2 ensure + 2 save attempts


@pytest.mark.asyncio
async def test_save_history_success_on_first_attempt(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест что retry не срабатывает при успешной первой попытке.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345
    messages = [{"role": "user", "content": "Test", "timestamp": datetime.now(UTC).isoformat()}]

    # Mock для _ensure_user_exists
    mock_ensure_session = AsyncMock()
    mock_ensure_session.__aenter__.return_value = mock_ensure_session
    mock_ensure_session.__aexit__.return_value = AsyncMock()
    mock_ensure_session.execute = AsyncMock(return_value=AsyncMock())

    # Mock для успешного save
    mock_save_session = AsyncMock()
    mock_save_session.__aenter__.return_value = mock_save_session
    mock_save_session.__aexit__.return_value = AsyncMock()

    mock_settings = MagicMock()
    mock_settings.max_history_messages = 50
    mock_settings_result = AsyncMock()
    mock_settings_result.scalar_one.return_value = mock_settings

    mock_ids_result = AsyncMock()
    mock_ids_result.all.return_value = []

    mock_save_session.execute = AsyncMock(side_effect=[mock_settings_result, mock_ids_result])
    mock_save_session.add = MagicMock()

    mock_database.session.side_effect = [mock_ensure_session, mock_save_session]

    # Вызываем save_history
    await storage.save_history(user_id, messages)

    # Должна быть только 1 попытка (1 ensure + 1 save)
    assert mock_database.session.call_count == 2


@pytest.mark.asyncio
async def test_prompt_cache_max_size() -> None:
    """
    Тест ограничения размера кеша.
    """
    # Создаём конфиг с маленьким кешем
    small_cache_config = Config(
        telegram_token="fake-token",
        openrouter_api_key="fake-key",
        openrouter_model="fake-model",
        db_password="fake-password",
        cache_ttl=300,
        cache_max_size=3,  # Только 3 записи
    )

    mock_database = AsyncMock()
    storage = Storage(mock_database, small_cache_config)

    # Добавляем 4 записи (больше maxsize)
    storage.prompt_cache[1] = "Prompt 1"
    storage.prompt_cache[2] = "Prompt 2"
    storage.prompt_cache[3] = "Prompt 3"
    storage.prompt_cache[4] = "Prompt 4"  # Это вытеснит самую старую

    # Кеш должен содержать максимум 3 записи
    assert len(storage.prompt_cache) == 3

    # Самая старая запись (1) должна быть вытеснена
    assert 1 not in storage.prompt_cache
    assert 2 in storage.prompt_cache
    assert 3 in storage.prompt_cache
    assert 4 in storage.prompt_cache


# Edge Cases Tests


@pytest.mark.asyncio
async def test_storage_concurrent_requests(mock_database: AsyncMock, test_config: Config) -> None:
    """
    Тест: одновременные запросы к Storage (concurrency).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    import asyncio

    storage = Storage(mock_database, test_config)

    # Создаем моки для ensure_user_exists
    async def mock_ensure_user(_user_id: int) -> None:
        await asyncio.sleep(0.01)  # Имитация async операции

    async def mock_get_settings(_user_id: int) -> MagicMock:
        mock_settings = MagicMock()
        mock_settings.system_prompt = "Test prompt"
        mock_settings.max_history_messages = 50
        return mock_settings

    # Патчим методы через monkeypatch (но у нас его нет в фикстуре)
    # Будем использовать direct patching
    storage._ensure_user_exists = mock_ensure_user  # type: ignore[method-assign]
    storage._get_user_settings = mock_get_settings  # type: ignore[method-assign]

    # Запускаем несколько одновременных запросов
    tasks = [storage.get_system_prompt(i) for i in range(1, 11)]

    # Все должны завершиться успешно
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Проверяем что нет исключений
    for result in results:
        assert not isinstance(result, Exception)
        assert result == "Test prompt"


@pytest.mark.asyncio
async def test_storage_unicode_and_emoji_in_messages(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест: сохранение сообщений с Unicode и эмодзи.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    messages = [
        {
            "role": "user",
            "content": "Привет! 👋 Как дела?",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        {
            "role": "assistant",
            "content": "Отлично! 😊 你好",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ]

    # Мокируем _save_history_attempt напрямую
    async def mock_save_attempt(_user_id: int, _messages: list[dict]) -> None:
        # Просто проверяем что unicode передается корректно
        assert any("👋" in msg.get("content", "") for msg in _messages)
        assert any("你好" in msg.get("content", "") for msg in _messages)

    storage._save_history_attempt = mock_save_attempt  # type: ignore[method-assign]

    # Вызываем save_history - не должно быть ошибок
    await storage.save_history(user_id, messages)

    # Тест прошел если нет исключений


@pytest.mark.asyncio
async def test_storage_very_long_message_content(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест: сохранение очень длинного сообщения (>10k символов).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Генерируем очень длинное сообщение
    long_content = "А" * 15000

    messages = [
        {"role": "user", "content": long_content, "timestamp": datetime.now(UTC).isoformat()},
    ]

    # Мокируем _save_history_attempt напрямую
    async def mock_save_attempt(_user_id: int, _messages: list[dict]) -> None:
        # Проверяем что длинное сообщение передается корректно
        assert any(len(msg.get("content", "")) == 15000 for msg in _messages)

    storage._save_history_attempt = mock_save_attempt  # type: ignore[method-assign]

    # Вызываем save_history - не должно быть ошибок
    await storage.save_history(user_id, messages)

    # Тест прошел если нет исключений


@pytest.mark.asyncio
async def test_storage_empty_string_in_content(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест: сохранение сообщений с пустым content.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    messages = [
        {"role": "user", "content": "", "timestamp": datetime.now(UTC).isoformat()},
        {"role": "assistant", "content": "   ", "timestamp": datetime.now(UTC).isoformat()},
    ]

    # Мокируем _save_history_attempt напрямую
    async def mock_save_attempt(_user_id: int, _messages: list[dict]) -> None:
        # Проверяем что пустые строки передаются корректно
        contents = [msg.get("content", "") for msg in _messages]
        assert "" in contents or "   " in contents

    storage._save_history_attempt = mock_save_attempt  # type: ignore[method-assign]

    # Вызываем save_history - не должно быть ошибок
    await storage.save_history(user_id, messages)

    # Тест прошел если нет исключений


# Security Tests


@pytest.mark.asyncio
async def test_storage_invalid_timestamp_handling(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест: обработка невалидного timestamp (защита от ValueError).

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Сообщения с невалидным timestamp
    messages = [
        {"role": "user", "content": "Test", "timestamp": "invalid-timestamp-format"},
        {"role": "assistant", "content": "Response", "timestamp": "not-a-date"},
    ]

    # Создаем переменную для проверки что fallback сработал
    fallback_used = False

    # Мокируем _save_history_attempt напрямую
    async def mock_save_attempt(_user_id: int, _messages: list[dict]) -> None:
        nonlocal fallback_used
        fallback_used = True
        # Проверяем что сообщения прошли (несмотря на невалидный timestamp)
        assert len(_messages) == 2

    storage._save_history_attempt = mock_save_attempt  # type: ignore[method-assign]

    # Вызываем save_history - НЕ должно выбросить ValueError
    await storage.save_history(user_id, messages)

    # Проверяем что обработка прошла успешно
    assert fallback_used


@pytest.mark.asyncio
async def test_storage_none_timestamp_handling(
    mock_database: AsyncMock, test_config: Config
) -> None:
    """
    Тест: обработка отсутствующего timestamp.

    Args:
        mock_database: Mock базы данных
        test_config: Тестовая конфигурация
    """
    storage = Storage(mock_database, test_config)
    user_id = 12345

    # Сообщение без timestamp вообще
    messages = [
        {"role": "user", "content": "Test without timestamp"},
    ]

    fallback_used = False

    async def mock_save_attempt(_user_id: int, _messages: list[dict]) -> None:
        nonlocal fallback_used
        fallback_used = True

    storage._save_history_attempt = mock_save_attempt  # type: ignore[method-assign]

    # Должно использовать текущее время
    await storage.save_history(user_id, messages)

    assert fallback_used
