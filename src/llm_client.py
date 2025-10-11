"""Клиент для работы с LLM через OpenRouter API."""

import logging
import time

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from src.config import Config

logger = logging.getLogger(__name__)


class LLMAPIError(Exception):
    """Исключение для ошибок LLM API."""

    pass


class LLMClient:
    """
    Клиент для работы с LLM через OpenRouter API.

    Отвечает за:
    - Отправку запросов к LLM
    - Retry механизм при сбоях
    - Обработку ошибок API
    - Логирование использования токенов
    """

    def __init__(self, config: Config) -> None:
        """
        Инициализация LLM клиента.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.client = AsyncOpenAI(
            base_url=config.openrouter_base_url, api_key=config.openrouter_api_key
        )
        logger.info(
            f"LLMClient initialized: model={config.openrouter_model}, "
            f"temperature={config.llm_temperature}, max_tokens={config.llm_max_tokens}"
        )

    async def generate_response(self, messages: list[dict[str, str]], user_id: int) -> str:
        """
        Генерирует ответ LLM на основе истории диалога.

        Args:
            messages: История диалога в формате OpenAI (включая системный промпт)
                      [{"role": "system"|"user"|"assistant", "content": "..."}]
            user_id: ID пользователя для логирования

        Returns:
            Текст ответа от LLM

        Raises:
            LLMAPIError: При ошибке API после всех retry попыток
        """
        # Фильтруем сообщения для LLM API (оставляем только role и content)
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]

        logger.info(
            f"LLM request for user {user_id}: "
            f"model={self.config.openrouter_model}, messages={len(api_messages)}"
        )

        # Выполняем запрос с retry механизмом
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()

                response = await self.client.chat.completions.create(
                    model=self.config.openrouter_model,
                    messages=api_messages,  # type: ignore[arg-type]
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens,
                )

                elapsed_time = time.time() - start_time

                # Извлекаем ответ
                assistant_message = response.choices[0].message.content

                # Логируем использование токенов
                if response.usage:
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens

                    logger.info(
                        f"LLM response for user {user_id}: "
                        f"tokens(prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}), "
                        f"time={elapsed_time:.2f}s"
                    )
                else:
                    logger.info(f"LLM response for user {user_id}: time={elapsed_time:.2f}s")

                return assistant_message or ""

            except RateLimitError as e:
                logger.warning(
                    f"Rate limit error for user {user_id} (attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    await self._retry_delay(attempt)
                else:
                    # Проверяем нужен ли fallback
                    if self._should_try_fallback(e):
                        return await self._try_fallback_model(api_messages, user_id, e)
                    raise LLMAPIError("Rate limit exceeded") from e

            except APITimeoutError as e:
                logger.warning(
                    f"Timeout error for user {user_id} (attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    await self._retry_delay(attempt)
                else:
                    raise LLMAPIError("Request timeout") from e

            except APIConnectionError as e:
                logger.warning(
                    f"Connection error for user {user_id} (attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    await self._retry_delay(attempt)
                else:
                    raise LLMAPIError("Connection error") from e

            except APIError as e:
                logger.error(
                    f"API error for user {user_id} (attempt {attempt + 1}/{self.config.retry_attempts}): {e}",
                    exc_info=True,
                )
                if attempt < self.config.retry_attempts - 1:
                    await self._retry_delay(attempt)
                else:
                    # Проверяем нужен ли fallback
                    if self._should_try_fallback(e):
                        return await self._try_fallback_model(api_messages, user_id, e)
                    raise LLMAPIError(f"API error: {str(e)}") from e

            except Exception as e:
                logger.error(f"Unexpected error for user {user_id}: {e}", exc_info=True)
                raise LLMAPIError(f"Unexpected error: {str(e)}") from e

        # На случай, если цикл завершился без return (не должно происходить)
        raise LLMAPIError("Failed to get LLM response after all retries")

    async def _retry_delay(self, attempt: int) -> None:
        """
        Задержка перед повторной попыткой с экспоненциальным backoff.

        Args:
            attempt: Номер попытки (начиная с 0)
        """
        import asyncio

        delay = self.config.retry_delay * (2**attempt)
        logger.debug(f"Waiting {delay:.2f}s before retry...")
        await asyncio.sleep(delay)

    def _should_try_fallback(self, error: Exception) -> bool:
        """
        Определяет нужно ли пробовать fallback модель.

        Fallback используется только для:
        - RateLimitError (429) - превышен лимит запросов
        - APIError - серверные ошибки (500, 503)

        НЕ используется для:
        - APITimeoutError - timeout проблема сети
        - APIConnectionError - проблема соединения

        Args:
            error: Исключение которое произошло

        Returns:
            True если нужно попробовать fallback модель, False иначе
        """
        # Если fallback модель не настроена - не пытаемся
        if not self.config.openrouter_fallback_model:
            return False

        # Timeout и Connection errors НЕ триггерят fallback (проверяем первыми)
        if isinstance(error, APITimeoutError | APIConnectionError):
            return False

        # RateLimitError и APIError триггерят fallback
        return isinstance(error, RateLimitError | APIError)

    async def _try_fallback_model(
        self, api_messages: list[dict[str, str]], user_id: int, primary_error: Exception
    ) -> str:
        """
        Попытка запроса к fallback модели с retry механизмом.

        Args:
            api_messages: Сообщения для отправки
            user_id: ID пользователя
            primary_error: Ошибка от основной модели

        Returns:
            Ответ от fallback модели

        Raises:
            LLMAPIError: Если fallback модель также провалилась
        """
        fallback_model = self.config.openrouter_fallback_model

        # Гарантируем что fallback модель настроена (для type checker)
        if not fallback_model:
            raise LLMAPIError("Fallback model not configured")

        logger.warning(
            f"Primary model failed for user {user_id}: {primary_error}. "
            f"Trying fallback model: {fallback_model}"
        )

        # Retry механизм для fallback модели
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()

                response = await self.client.chat.completions.create(
                    model=fallback_model,
                    messages=api_messages,  # type: ignore[arg-type]
                    temperature=self.config.llm_temperature,
                    max_tokens=self.config.llm_max_tokens,
                )

                elapsed_time = time.time() - start_time

                # Извлекаем ответ
                assistant_message = response.choices[0].message.content

                # Логируем успешный fallback
                if response.usage:
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens

                    logger.info(
                        f"Fallback model succeeded for user {user_id}: "
                        f"model={fallback_model}, "
                        f"tokens(prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}), "
                        f"time={elapsed_time:.2f}s"
                    )
                else:
                    logger.info(
                        f"Fallback model succeeded for user {user_id}: "
                        f"model={fallback_model}, time={elapsed_time:.2f}s"
                    )

                return assistant_message or ""

            except Exception as e:
                logger.warning(
                    f"Fallback model error for user {user_id} "
                    f"(attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    await self._retry_delay(attempt)
                else:
                    # Fallback тоже провалился
                    logger.error(
                        f"Both models failed for user {user_id}. "
                        f"Primary: {primary_error}. Fallback: {e}"
                    )
                    raise LLMAPIError(
                        f"Both primary and fallback models failed. "
                        f"Primary: {str(primary_error)}. Fallback: {str(e)}"
                    ) from e

        # На случай, если цикл завершился без return (не должно происходить)
        raise LLMAPIError("Fallback model failed after all retries")
