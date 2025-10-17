"""Интеграционные тесты для handlers."""

from unittest.mock import AsyncMock

import pytest

from src.config import Config
from src.database import Database
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    mock_llm_client.generate_response.return_value = "Отлично, спасибо!"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    mock_storage.load_recent_history.assert_called_once()
    mock_llm_client.generate_response.assert_called_once()
    mock_storage.save_history.assert_called_once()
    mock_message.answer.assert_called_once_with("Отлично, спасибо!")


@pytest.mark.asyncio
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = existing_history
    mock_llm_client.generate_response.return_value = "Да, продолжаем!"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # История должна была загрузиться
    mock_storage.load_recent_history.assert_called_once()

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
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = []
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
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = []
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
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = []
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
@pytest.mark.integration
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
    mock_storage.load_recent_history.return_value = []
    mock_storage.get_system_prompt.return_value = None
    mock_llm_client.generate_response.return_value = "Ответ"

    # Execute
    await handle_message(mock_message, mock_bot, mock_llm_client, mock_storage, test_config)

    # Assert
    # Должен был быть вызван send_chat_action
    mock_bot.send_chat_action.assert_called_once()
    call_kwargs = mock_bot.send_chat_action.call_args.kwargs
    assert call_kwargs["chat_id"] == mock_message.chat.id


@pytest.mark.integration
class TestHandlersFallbackIntegration:
    """Интеграционные тесты fallback механизма."""

    @pytest.mark.asyncio
    async def test_handle_message_with_fallback_success(
        self,
        mock_message: AsyncMock,
        mock_bot: AsyncMock,
        test_config: Config,
        test_db_real: "Database",
    ) -> None:
        """
        Тест: хендлер использует fallback модель при провале основной.

        Args:
            mock_message: Mock сообщения от пользователя
            mock_bot: Mock бота
            test_config: Тестовая конфигурация
            test_db_real: Реальная тестовая БД
        """
        # Arrange: настраиваем fallback модель
        test_config.openrouter_fallback_model = "meta-llama/llama-3.1-8b-instruct:free"

        # Создаём реальные компоненты с реальной БД
        from src.llm_client import LLMClient
        from src.storage import Storage

        llm_client = LLMClient(test_config)
        storage = Storage(test_db_real, test_config)

        mock_message.text = "Привет!"

        # Mock OpenAI client: основная модель падает, fallback работает
        mock_openai = AsyncMock()
        mock_response_fallback = AsyncMock()
        mock_response_fallback.choices = [AsyncMock()]
        mock_response_fallback.choices[0].message.content = "Ответ от fallback модели"
        mock_response_fallback.usage.total_tokens = 50

        from openai import RateLimitError

        # Основная модель провалится 3 раза, затем fallback сработает
        mock_openai.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            mock_response_fallback,  # fallback успешен
        ]

        llm_client.client = mock_openai

        # Act: вызываем handler
        from src.handlers.messages import handle_message

        await handle_message(mock_message, mock_bot, llm_client, storage, test_config)

        # Assert: пользователь получил ответ от fallback модели
        mock_message.answer.assert_called_once_with("Ответ от fallback модели")

        # Проверяем что было 4 вызова (3 основной + 1 fallback)
        assert mock_openai.chat.completions.create.call_count == 4

    @pytest.mark.asyncio
    async def test_handle_message_both_models_fail(
        self,
        mock_message: AsyncMock,
        mock_bot: AsyncMock,
        test_config: Config,
        test_db_real: "Database",
    ) -> None:
        """
        Тест: хендлер обрабатывает провал обеих моделей.

        Args:
            mock_message: Mock сообщения от пользователя
            mock_bot: Mock бота
            test_config: Тестовая конфигурация
            test_db_real: Реальная тестовая БД
        """
        # Arrange: настраиваем fallback модель
        test_config.openrouter_fallback_model = "meta-llama/llama-3.1-8b-instruct:free"

        from src.llm_client import LLMClient
        from src.storage import Storage

        llm_client = LLMClient(test_config)
        storage = Storage(test_db_real, test_config)

        mock_message.text = "Тест"

        # Mock: обе модели падают
        mock_openai = AsyncMock()
        from openai import RateLimitError

        # 3 попытки основной + 3 попытки fallback = 6 провалов
        mock_openai.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
        ]

        llm_client.client = mock_openai

        # Act
        from src.handlers.messages import handle_message

        await handle_message(mock_message, mock_bot, llm_client, storage, test_config)

        # Assert: пользователь получил сообщение об ошибке
        mock_message.answer.assert_called_once()
        error_message = mock_message.answer.call_args[0][0]

        # Проверяем что это понятное сообщение об ошибке (не технические детали)
        assert "⏳" in error_message or "лимит" in error_message.lower()
        # Не должно быть упоминания о fallback в сообщении пользователю
        assert "fallback" not in error_message.lower()
        assert "резерв" not in error_message.lower()

        # Проверяем количество попыток: 3 основной + 3 fallback
        assert mock_openai.chat.completions.create.call_count == 6

    @pytest.mark.asyncio
    async def test_end_to_end_fallback_flow(
        self,
        mock_message: AsyncMock,
        mock_bot: AsyncMock,
        test_config: Config,
        test_db_real: "Database",
    ) -> None:
        """
        Тест: полный флоу с Storage - fallback ответ сохраняется корректно.

        Args:
            mock_message: Mock сообщения
            mock_bot: Mock бота
            test_config: Тестовая конфигурация
        """
        # Arrange
        test_config.openrouter_fallback_model = "meta-llama/llama-3.1-8b-instruct:free"

        from src.llm_client import LLMClient
        from src.storage import Storage

        llm_client = LLMClient(test_config)
        storage = Storage(test_db_real, test_config)

        user_id = 12345
        mock_message.from_user.id = user_id
        mock_message.text = "Тестовое сообщение"

        # Mock: основная падает, fallback работает
        mock_openai = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Fallback ответ"
        mock_response.usage.total_tokens = 40

        from openai import RateLimitError

        mock_openai.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            mock_response,
        ]

        llm_client.client = mock_openai

        # Act: полный флоу через handler
        from src.handlers.messages import handle_message

        await handle_message(mock_message, mock_bot, llm_client, storage, test_config)

        # Assert: история сохранена с fallback ответом
        history = await storage.load_history(user_id)

        # Проверяем что в истории есть user и assistant сообщения
        assert len(history) >= 2

        # Последние 2 сообщения должны быть user и assistant
        assert history[-2]["role"] == "user"
        assert history[-2]["content"] == "Тестовое сообщение"
        assert history[-1]["role"] == "assistant"
        assert history[-1]["content"] == "Fallback ответ"

        # Пользователь получил ответ
        mock_message.answer.assert_called_once_with("Fallback ответ")

    @pytest.mark.asyncio
    async def test_fallback_preserves_conversation_context(
        self,
        mock_message: AsyncMock,
        mock_bot: AsyncMock,
        test_config: Config,
        test_db_real: "Database",
    ) -> None:
        """
        Тест: fallback сохраняет контекст диалога.

        Args:
            mock_message: Mock сообщения
            mock_bot: Mock бота
            test_config: Тестовая конфигурация
        """
        # Arrange
        test_config.openrouter_fallback_model = "meta-llama/llama-3.1-8b-instruct:free"

        from src.llm_client import LLMClient
        from src.storage import Storage

        llm_client = LLMClient(test_config)
        storage = Storage(test_db_real, test_config)

        user_id = 12345
        mock_message.from_user.id = user_id

        # Сначала сохраняем существующую историю
        existing_history = [
            {"role": "system", "content": "Ты помощник", "timestamp": "2024-01-01T00:00:00+00:00"},
            {
                "role": "user",
                "content": "Как тебя зовут?",
                "timestamp": "2024-01-01T00:00:01+00:00",
            },
            {
                "role": "assistant",
                "content": "Я AI ассистент",
                "timestamp": "2024-01-01T00:00:02+00:00",
            },
        ]
        await storage.save_history(user_id, existing_history)

        mock_message.text = "А сколько тебе лет?"

        # Mock: основная падает, fallback работает
        mock_openai = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Я не имею возраста"
        mock_response.usage.total_tokens = 35

        from openai import RateLimitError

        mock_openai.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            mock_response,
        ]

        llm_client.client = mock_openai

        # Act
        from src.handlers.messages import handle_message

        await handle_message(mock_message, mock_bot, llm_client, storage, test_config)

        # Assert: контекст сохранён
        history = await storage.load_history(user_id)

        # Проверяем что история содержит все сообщения
        assert len(history) == 5  # 3 старых + 1 user + 1 assistant

        # Старый контекст сохранён
        assert history[0]["role"] == "system"
        assert history[1]["role"] == "user"
        assert history[1]["content"] == "Как тебя зовут?"
        assert history[2]["role"] == "assistant"
        assert history[2]["content"] == "Я AI ассистент"

        # Новые сообщения добавлены
        assert history[3]["role"] == "user"
        assert history[3]["content"] == "А сколько тебе лет?"
        assert history[4]["role"] == "assistant"
        assert history[4]["content"] == "Я не имею возраста"

    @pytest.mark.asyncio
    async def test_user_sees_no_fallback_details(
        self,
        mock_message: AsyncMock,
        mock_bot: AsyncMock,
        test_config: Config,
        test_db_real: "Database",
    ) -> None:
        """
        Тест: пользователь НЕ видит технические детали fallback.

        Args:
            mock_message: Mock сообщения
            mock_bot: Mock бота
            test_config: Тестовая конфигурация
            test_db_real: Реальная тестовая БД
        """
        # Arrange
        test_config.openrouter_fallback_model = "meta-llama/llama-3.1-8b-instruct:free"

        from src.llm_client import LLMClient
        from src.storage import Storage

        llm_client = LLMClient(test_config)
        storage = Storage(test_db_real, test_config)

        mock_message.text = "Привет"

        # Mock: основная падает, fallback работает
        mock_openai = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Здравствуй!"
        mock_response.usage.total_tokens = 20

        from openai import RateLimitError

        mock_openai.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            RateLimitError("Rate limit", response=AsyncMock(status_code=429), body=None),
            mock_response,
        ]

        llm_client.client = mock_openai

        # Act
        from src.handlers.messages import handle_message

        await handle_message(mock_message, mock_bot, llm_client, storage, test_config)

        # Assert: ответ НЕ содержит технических деталей
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]

        # Пользователь просто получает ответ
        assert response_text == "Здравствуй!"

        # Нет упоминаний о fallback
        assert "fallback" not in response_text.lower()
        assert "резерв" not in response_text.lower()
        assert "основная модель" not in response_text.lower()
        assert "попытка" not in response_text.lower()
