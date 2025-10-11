"""Фикстуры для тестов."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.config import Config


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

    # Создаём и возвращаем конфигурацию
    return Config()


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """
    Создаёт mock-ответ от OpenAI API.

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
def mock_openai_client(mock_openai_response: dict[str, Any]) -> AsyncMock:
    """
    Создаёт mock AsyncOpenAI клиента.

    Args:
        mock_openai_response: Mock-ответ от API

    Returns:
        AsyncMock объект клиента
    """
    mock_client = AsyncMock()

    # Создаём структуру ответа
    mock_choice = AsyncMock()
    mock_choice.message.content = mock_openai_response["choices"][0]["message"]["content"]

    mock_completion = AsyncMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage.prompt_tokens = mock_openai_response["usage"]["prompt_tokens"]
    mock_completion.usage.completion_tokens = mock_openai_response["usage"]["completion_tokens"]
    mock_completion.usage.total_tokens = mock_openai_response["usage"]["total_tokens"]

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
