"""Фикстуры для тестов."""

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.config import Config
from src.database import Database


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """
    Создаёт временную директорию для данных тестов.

    Args:
        tmp_path: Временная директория от pytest

    Returns:
        Путь к тестовой директории данных
    """
    data_dir = tmp_path / "test_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def test_config(temp_data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    """
    Создаёт тестовую конфигурацию с временной директорией.

    Args:
        temp_data_dir: Временная директория для данных
        monkeypatch: Фикстура для изменения переменных окружения

    Returns:
        Объект Config с тестовыми настройками
    """
    # Устанавливаем переменные окружения для тестов
    monkeypatch.setenv("TELEGRAM_TOKEN", "test_token_123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_openrouter_key_abc123")
    monkeypatch.setenv("DATA_DIR", str(temp_data_dir))
    monkeypatch.setenv("DB_PASSWORD", "test")

    # Создаём и возвращаем конфигурацию
    return Config()


@pytest.fixture
def mock_database() -> AsyncMock:
    """
    Создаёт mock Database для unit-тестов Storage.

    Returns:
        AsyncMock объект Database с мокированным session context manager
    """
    database = AsyncMock(spec=Database)

    # Мокируем session context manager
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.add = AsyncMock()

    # Настраиваем context manager
    database.session.return_value.__aenter__.return_value = mock_session
    database.session.return_value.__aexit__.return_value = None

    return database


@pytest.fixture
async def test_db_real(test_config: Config) -> AsyncGenerator[Database, None]:
    """
    Создаёт реальную тестовую БД (SQLite in-memory) для интеграционных тестов.

    Args:
        test_config: Тестовая конфигурация

    Yields:
        Database с реальной БД для полной интеграции
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from src.models import Base  # Импорт Base здесь

    # Создаём in-memory SQLite БД для интеграционных тестов
    test_db = Database.__new__(Database)
    test_db.config = test_config
    test_db.engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    test_db.session_factory = async_sessionmaker(
        test_db.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Создаём все таблицы
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_db

    # Cleanup
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_db.engine.dispose()


@pytest.fixture
def sample_openai_response() -> dict[str, Any]:
    """
    Создаёт пример ответа от OpenAI API для тестов.

    Returns:
        Словарь с данными ответа API
    """
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "openai/gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Это тестовый ответ от LLM."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
    }


@pytest.fixture
def mock_openai_client(sample_openai_response: dict[str, Any]) -> AsyncMock:
    """
    Создаёт mock AsyncOpenAI клиента.

    Args:
        sample_openai_response: Пример ответа от API

    Returns:
        AsyncMock объект клиента
    """
    mock_client = AsyncMock()

    # Создаём структуру ответа
    mock_choice = AsyncMock()
    mock_choice.message.content = sample_openai_response["choices"][0]["message"]["content"]

    mock_completion = AsyncMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage.prompt_tokens = sample_openai_response["usage"]["prompt_tokens"]
    mock_completion.usage.completion_tokens = sample_openai_response["usage"]["completion_tokens"]
    mock_completion.usage.total_tokens = sample_openai_response["usage"]["total_tokens"]

    # Настраиваем mock
    mock_client.chat.completions.create.return_value = mock_completion

    return mock_client


@pytest.fixture
def sample_messages() -> list[dict[str, str]]:
    """
    Создаёт примеры сообщений для тестов.

    Returns:
        Список сообщений в формате истории диалога
    """
    return [
        {
            "role": "system",
            "content": "Ты полезный ассистент.",
            "timestamp": "2024-01-01T00:00:00.000000+00:00",
        },
        {
            "role": "user",
            "content": "Привет!",
            "timestamp": "2024-01-01T00:00:01.000000+00:00",
        },
        {
            "role": "assistant",
            "content": "Здравствуйте! Чем могу помочь?",
            "timestamp": "2024-01-01T00:00:02.000000+00:00",
        },
    ]


@pytest.fixture
def mock_user() -> AsyncMock:
    """
    Создаёт mock User объект для тестов handlers.

    Returns:
        AsyncMock объект пользователя Telegram
    """
    user = AsyncMock()
    user.id = 12345
    user.first_name = "Test User"
    user.username = "testuser"
    return user


@pytest.fixture
def mock_chat() -> AsyncMock:
    """
    Создаёт mock Chat объект для тестов handlers.

    Returns:
        AsyncMock объект чата Telegram
    """
    chat = AsyncMock()
    chat.id = 12345
    chat.type = "private"
    return chat


@pytest.fixture
def mock_message(mock_user: AsyncMock, mock_chat: AsyncMock) -> AsyncMock:
    """
    Создаёт mock Message объект для тестов handlers.

    Args:
        mock_user: Mock пользователя
        mock_chat: Mock чата

    Returns:
        AsyncMock объект сообщения Telegram
    """
    message = AsyncMock()
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "/test"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_bot() -> AsyncMock:
    """
    Создаёт mock Bot объект для тестов handlers.

    Returns:
        AsyncMock объект бота Telegram
    """
    bot = AsyncMock()
    bot.send_chat_action = AsyncMock()
    return bot


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """
    Создаёт mock LLMClient для тестов handlers.

    Returns:
        AsyncMock объект LLMClient
    """
    client = AsyncMock()
    client.generate_response = AsyncMock(return_value="Mock LLM response")
    return client


@pytest.fixture
def mock_storage() -> AsyncMock:
    """
    Создаёт mock Storage для тестов handlers.

    Returns:
        AsyncMock объект Storage
    """
    storage = AsyncMock()
    storage.load_history = AsyncMock(return_value=[])
    storage.save_history = AsyncMock()
    storage.get_system_prompt = AsyncMock(return_value=None)
    storage.set_system_prompt = AsyncMock()
    storage.get_dialog_info = AsyncMock(
        return_value={
            "messages_count": 0,
            "system_prompt": None,
            "updated_at": None,
        }
    )
    return storage
