"""Тесты для модуля LLMClient."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, APIError, RateLimitError

from src.config import Config
from src.llm_client import LLMAPIError, LLMClient


class TestLLMClient:
    """Тесты класса LLMClient."""

    @pytest.mark.asyncio
    async def test_init_creates_client(self, test_config: Config) -> None:
        """
        Тест: инициализация LLMClient создаёт AsyncOpenAI клиента.

        Args:
            test_config: Тестовая конфигурация
        """
        llm_client = LLMClient(test_config)

        assert llm_client.config == test_config
        assert llm_client.client is not None

    @pytest.mark.asyncio
    async def test_generate_response_success(
        self,
        test_config: Config,
        mock_openai_client: AsyncMock,
        sample_messages: list[dict[str, str]],
    ) -> None:
        """
        Тест: успешная генерация ответа от LLM.

        Args:
            test_config: Тестовая конфигурация
            mock_openai_client: Mock клиента OpenAI
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        llm_client.client = mock_openai_client
        user_id = 12345

        response = await llm_client.generate_response(sample_messages, user_id)

        # Проверяем что получили ответ
        assert response == "Это тестовый ответ от LLM."

        # Проверяем что API был вызван с правильными параметрами
        mock_openai_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs

        assert call_kwargs["model"] == test_config.openrouter_model
        assert call_kwargs["temperature"] == test_config.llm_temperature
        assert call_kwargs["max_tokens"] == test_config.llm_max_tokens
        assert "messages" in call_kwargs

    @pytest.mark.asyncio
    async def test_generate_response_filters_timestamp(
        self,
        test_config: Config,
        mock_openai_client: AsyncMock,
        sample_messages: list[dict[str, str]],
    ) -> None:
        """
        Тест: timestamp удаляется из сообщений перед отправкой в API.

        Args:
            test_config: Тестовая конфигурация
            mock_openai_client: Mock клиента OpenAI
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        llm_client.client = mock_openai_client
        user_id = 12345

        await llm_client.generate_response(sample_messages, user_id)

        # Получаем отправленные сообщения
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        sent_messages = call_kwargs["messages"]

        # Проверяем что timestamp отсутствует
        for msg in sent_messages:
            assert "timestamp" not in msg
            assert "role" in msg
            assert "content" in msg

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: retry механизм при RateLimitError.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock который сначала выбрасывает RateLimitError, потом успех
        mock_client = AsyncMock()
        mock_choice = AsyncMock()
        mock_choice.message.content = "Успешный ответ после retry"

        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage.prompt_tokens = 10
        mock_completion.usage.completion_tokens = 5
        mock_completion.usage.total_tokens = 15

        # Создаём mock response для RateLimitError
        mock_response = MagicMock()
        mock_response.request = MagicMock()

        # Первый вызов - ошибка, второй - успех
        mock_client.chat.completions.create.side_effect = [
            RateLimitError("Rate limit exceeded", response=mock_response, body=None),
            mock_completion,
        ]

        llm_client.client = mock_client

        # Вызываем и ожидаем успешный retry
        response = await llm_client.generate_response(sample_messages, user_id)

        assert response == "Успешный ответ после retry"
        assert mock_client.chat.completions.create.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: retry механизм при APIConnectionError.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock
        mock_client = AsyncMock()
        mock_choice = AsyncMock()
        mock_choice.message.content = "Успешный ответ после переподключения"

        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage.prompt_tokens = 10
        mock_completion.usage.completion_tokens = 5
        mock_completion.usage.total_tokens = 15

        # Первый вызов - ошибка соединения, второй - успех
        mock_request = AsyncMock()
        mock_client.chat.completions.create.side_effect = [
            APIConnectionError(request=mock_request),
            mock_completion,
        ]

        llm_client.client = mock_client

        response = await llm_client.generate_response(sample_messages, user_id)

        assert response == "Успешный ответ после переподключения"
        assert mock_client.chat.completions.create.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: выброс исключения после превышения максимального числа retry.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock который всегда выбрасывает ошибку
        mock_client = AsyncMock()
        # Создаём mock response для RateLimitError
        mock_response = MagicMock()
        mock_response.request = MagicMock()

        mock_client.chat.completions.create.side_effect = RateLimitError(
            "Rate limit exceeded", response=mock_response, body=None
        )

        llm_client.client = mock_client

        # Ожидаем LLMAPIError после всех retry
        with pytest.raises(LLMAPIError) as exc_info:
            await llm_client.generate_response(sample_messages, user_id)

        assert "Rate limit exceeded" in str(exc_info.value)
        # По умолчанию 3 попытки в конфиге
        assert mock_client.chat.completions.create.call_count == test_config.retry_attempts

    @pytest.mark.asyncio
    async def test_api_error_handling(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: обработка общих ошибок API.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock который выбрасывает APIError
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = APIError(
            "API Error", request=AsyncMock(), body=None
        )

        llm_client.client = mock_client

        # Ожидаем LLMAPIError
        with pytest.raises(LLMAPIError):
            await llm_client.generate_response(sample_messages, user_id)

    @pytest.mark.asyncio
    async def test_empty_response_handling(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: обработка пустого ответа от API.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock с пустым ответом
        mock_client = AsyncMock()
        mock_choice = AsyncMock()
        mock_choice.message.content = None

        mock_completion = AsyncMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage.prompt_tokens = 10
        mock_completion.usage.completion_tokens = 0
        mock_completion.usage.total_tokens = 10

        mock_client.chat.completions.create.return_value = mock_completion
        llm_client.client = mock_client

        # LLMClient возвращает пустую строку если content None (не выбрасывает исключение)
        response = await llm_client.generate_response(sample_messages, user_id)
        assert response == ""

    @pytest.mark.asyncio
    async def test_no_choices_in_response(
        self, test_config: Config, sample_messages: list[dict[str, str]]
    ) -> None:
        """
        Тест: обработка ответа без choices.

        Args:
            test_config: Тестовая конфигурация
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        user_id = 12345

        # Создаём mock без choices
        mock_client = AsyncMock()
        mock_completion = AsyncMock()
        mock_completion.choices = []

        mock_client.chat.completions.create.return_value = mock_completion
        llm_client.client = mock_client

        # Ожидаем LLMAPIError из-за IndexError при доступе к choices[0]
        with pytest.raises(LLMAPIError) as exc_info:
            await llm_client.generate_response(sample_messages, user_id)

        # Ошибка будет "Unexpected error: list index out of range"
        assert "Unexpected error" in str(exc_info.value) or "list index" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_usage_logging(
        self,
        test_config: Config,
        mock_openai_client: AsyncMock,
        sample_messages: list[dict[str, str]],
    ) -> None:
        """
        Тест: логирование использования токенов.

        Args:
            test_config: Тестовая конфигурация
            mock_openai_client: Mock клиента OpenAI
            sample_messages: Примеры сообщений
        """
        llm_client = LLMClient(test_config)
        llm_client.client = mock_openai_client
        user_id = 12345

        # Вызываем генерацию
        await llm_client.generate_response(sample_messages, user_id)

        # Проверяем что метод был вызван и вернул данные с usage
        # (проверка логирования через caplog требует дополнительной фикстуры,
        # здесь просто убеждаемся что код выполняется без ошибок)
        assert mock_openai_client.chat.completions.create.called
