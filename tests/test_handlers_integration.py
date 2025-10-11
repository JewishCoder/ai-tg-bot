"""Интеграционные тесты для handlers."""

from unittest.mock import AsyncMock

import pytest

from src.config import Config
from src.handlers.commands import (
    handle_help,
    handle_reset,
    handle_role,
    handle_start,
    handle_status,
)
from src.handlers.messages import handle_message
from src.llm_client import LLMAPIError


@pytest.mark.asyncio
async def test_handle_start_command(mock_message: AsyncMock) -> None:
    """Тест: команда /start отправляет приветствие."""
    await handle_start(mock_message)

    # Проверяем что ответ был отправлен
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]

    # Проверяем содержание приветствия
    assert "Привет" in call_args or "👋" in call_args
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/reset" in call_args


@pytest.mark.asyncio
async def test_handle_help_command(mock_message: AsyncMock) -> None:
    """Тест: команда /help отправляет справку."""
    await handle_help(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]

    # Проверяем что справка содержит все команды
    assert "/start" in call_args
    assert "/help" in call_args
    assert "/reset" in call_args
    assert "/role" in call_args
    assert "/status" in call_args


@pytest.mark.asyncio
async def test_handle_role_without_args(
    mock_message: AsyncMock, mock_bot: AsyncMock, mock_storage: AsyncMock, test_config: Config
) -> None:
    """Тест: команда /role без аргументов возвращает ошибку."""
    mock_message.text = "/role"

    await handle_role(mock_message, mock_bot, mock_storage, test_config)

    # Должно быть сообщение об ошибке
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "❌" in call_args or "Неправильное использование" in call_args


@pytest.mark.asyncio
async def test_handle_role_default(
    mock_message: AsyncMock, mock_bot: AsyncMock, mock_storage: AsyncMock, test_config: Config
) -> None:
    """Тест: команда /role default возвращает к дефолтной роли."""
    mock_message.text = "/role default"

    await handle_role(mock_message, mock_bot, mock_storage, test_config)

    # Проверяем что был вызван set_system_prompt с дефолтным промптом
    mock_storage.set_system_prompt.assert_called_once()
    args = mock_storage.set_system_prompt.call_args[0]
    assert args[1] == test_config.system_prompt

    # Проверяем ответ пользователю
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "✅" in call_args or "успешно" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_role_custom(
    mock_message: AsyncMock, mock_bot: AsyncMock, mock_storage: AsyncMock, test_config: Config
) -> None:
    """Тест: команда /role с кастомным промптом устанавливает его."""
    custom_prompt = "Ты опытный Python разработчик"
    mock_message.text = f"/role {custom_prompt}"

    await handle_role(mock_message, mock_bot, mock_storage, test_config)

    # Проверяем что был вызван set_system_prompt с кастомным промптом
    mock_storage.set_system_prompt.assert_called_once()
    args = mock_storage.set_system_prompt.call_args[0]
    assert args[1] == custom_prompt

    # Проверяем ответ
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "✅" in call_args or "успешно" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_status_command(
    mock_message: AsyncMock, mock_bot: AsyncMock, mock_storage: AsyncMock, test_config: Config
) -> None:
    """Тест: команда /status возвращает статистику."""
    await handle_status(mock_message, mock_bot, mock_storage, test_config)

    # Проверяем что был запрос информации о диалоге
    mock_storage.get_dialog_info.assert_called_once_with(12345)

    # Проверяем ответ
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Статус" in call_args or "📊" in call_args


@pytest.mark.asyncio
async def test_handle_reset_command(
    mock_message: AsyncMock, mock_bot: AsyncMock, mock_storage: AsyncMock, test_config: Config
) -> None:
    """Тест: команда /reset очищает историю."""
    await handle_reset(mock_message, mock_bot, mock_storage, test_config)

    # Проверяем что был вызван get_system_prompt и set_system_prompt
    mock_storage.get_system_prompt.assert_called_once()
    mock_storage.set_system_prompt.assert_called_once()

    # Проверяем ответ
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "✅" in call_args or "очищена" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_full_cycle(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: полный цикл обработки сообщения."""
    # Setup
    mock_message.text = "Привет, как дела?"
    mock_storage.load_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    mock_llm_client.generate_response.return_value = "Отлично, спасибо!"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    mock_storage.load_history.assert_called_once_with(12345)
    mock_llm_client.generate_response.assert_called_once()
    mock_storage.save_history.assert_called_once()
    mock_message.answer.assert_called_once_with("Отлично, спасибо!")


@pytest.mark.asyncio
async def test_handle_message_with_existing_history(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: обработка сообщения с существующей историей."""
    # Setup
    mock_message.text = "Продолжаем разговор"
    existing_history = [
        {"role": "system", "content": "Ты помощник", "timestamp": "2024-01-01T00:00:00+00:00"},
        {"role": "user", "content": "Привет", "timestamp": "2024-01-01T00:00:01+00:00"},
        {
            "role": "assistant",
            "content": "Здравствуй",
            "timestamp": "2024-01-01T00:00:02+00:00",
        },
    ]
    mock_storage.load_history.return_value = existing_history
    mock_llm_client.generate_response.return_value = "Да, продолжаем!"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # История должна была загрузиться
    mock_storage.load_history.assert_called_once_with(12345)

    # LLM должен был быть вызван
    mock_llm_client.generate_response.assert_called_once()

    # История должна была сохраниться с новым сообщением и ответом
    # 3 старых + 1 user + 1 assistant = 5 сообщений в итоге
    mock_storage.save_history.assert_called_once()
    saved_history = mock_storage.save_history.call_args[0][1]
    assert len(saved_history) == 5
    # Предпоследнее - user, последнее - assistant
    assert saved_history[-2]["role"] == "user"
    assert saved_history[-2]["content"] == "Продолжаем разговор"
    assert saved_history[-1]["role"] == "assistant"
    assert saved_history[-1]["content"] == "Да, продолжаем!"


@pytest.mark.asyncio
async def test_handle_message_llm_error(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: обработка ошибки LLM API."""
    # Setup
    mock_message.text = "Тестовое сообщение"
    mock_storage.load_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    mock_llm_client.generate_response.side_effect = LLMAPIError("Rate limit exceeded")

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # Должно быть отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    # Проверяем что это отформатированная ошибка
    assert "⏳" in call_args or "лимит" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_long_response(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: обработка длинного ответа (разбивка на части)."""
    # Setup
    mock_message.text = "Расскажи много"
    mock_storage.load_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    # Создаём длинный ответ > 4096 символов
    long_response = "a" * 5000
    mock_llm_client.generate_response.return_value = long_response

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # Должно быть несколько вызовов answer (для разных частей)
    assert mock_message.answer.call_count >= 2

    # Первый вызов должен содержать индикатор части
    first_call = mock_message.answer.call_args_list[0][0][0]
    assert "Часть" in first_call or "📄" in first_call


@pytest.mark.asyncio
async def test_handle_message_custom_system_prompt(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: использование кастомного системного промпта."""
    # Setup
    mock_message.text = "Тест"
    mock_storage.load_history.return_value = []
    custom_prompt = "Ты эксперт по Python"
    mock_storage.get_system_prompt.return_value = custom_prompt
    mock_llm_client.generate_response.return_value = "Ответ"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # LLM должен был получить кастомный промпт
    call_args = mock_llm_client.generate_response.call_args
    messages = call_args.kwargs["messages"]
    # Первое сообщение должно быть system с кастомным промптом
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == custom_prompt


@pytest.mark.asyncio
async def test_handle_message_chat_action(
    mock_message: AsyncMock,
    mock_bot: AsyncMock,
    mock_llm_client: AsyncMock,
    mock_storage: AsyncMock,
    test_config: Config,
) -> None:
    """Тест: бот отправляет chat action (typing) при обработке."""
    # Setup
    mock_message.text = "Тест"
    mock_storage.load_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    mock_llm_client.generate_response.return_value = "Ответ"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # Должен был быть вызван send_chat_action
    mock_bot.send_chat_action.assert_called_once()
    call_kwargs = mock_bot.send_chat_action.call_args.kwargs
    assert call_kwargs["chat_id"] == mock_message.chat.id
