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
