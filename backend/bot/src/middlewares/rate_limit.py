"""Rate limiting middleware для защиты от спама."""

import logging
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов пользователей.

    Защищает от спама и злоупотреблений, отслеживая количество запросов
    каждого пользователя в заданный период времени.

    Attributes:
        rate: Максимальное количество запросов
        per: Период времени в секундах
        user_requests: Словарь с timestamps запросов для каждого пользователя
    """

    def __init__(self, rate: int = 10, per: float = 60.0, enabled: bool = True) -> None:
        """
        Инициализация rate limiter.

        Args:
            rate: Максимальное количество запросов (по умолчанию 10)
            per: Период времени в секундах (по умолчанию 60.0)
            enabled: Включен ли rate limiting (по умолчанию True)
        """
        self.rate = rate
        self.per = per
        self.enabled = enabled
        self.user_requests: dict[int, list[float]] = defaultdict(list)

        logger.info(f"RateLimitMiddleware initialized: rate={rate}, per={per}s, enabled={enabled}")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Обрабатывает входящее событие с проверкой rate limit.

        Args:
            handler: Следующий обработчик в цепочке
            event: Событие Telegram (обычно Message)
            data: Дополнительные данные

        Returns:
            Результат обработки или None при превышении лимита
        """
        # Если rate limiting отключен, пропускаем проверку
        if not self.enabled:
            return await handler(event, data)

        # Обрабатываем только сообщения
        if not isinstance(event, Message):
            return await handler(event, data)

        message: Message = event
        user_id = message.from_user.id if message.from_user else None

        if user_id is None:
            # Если нет user_id, пропускаем (не должно происходить в нормальных условиях)
            logger.warning("Message without user_id, skipping rate limit check")
            return await handler(event, data)

        current_time = time.time()

        # Получаем timestamps запросов пользователя
        user_timestamps = self.user_requests[user_id]

        # Удаляем старые timestamps (вышедшие за пределы периода)
        user_timestamps[:] = [ts for ts in user_timestamps if current_time - ts < self.per]

        # Проверяем лимит
        if len(user_timestamps) >= self.rate:
            # Вычисляем время до следующего доступного запроса
            oldest_timestamp = user_timestamps[0]
            wait_time = int(self.per - (current_time - oldest_timestamp)) + 1

            logger.warning(
                f"User {user_id}: rate limit exceeded "
                f"({len(user_timestamps)}/{self.rate} requests in {self.per}s)"
            )

            # Отправляем сообщение пользователю
            await message.answer(
                f"⚠️ Слишком много запросов.\n\n"
                f"Пожалуйста, подождите {wait_time} секунд перед следующим сообщением.",
                parse_mode=None,
            )

            # Не вызываем handler - блокируем запрос
            return None

        # Добавляем текущий timestamp
        user_timestamps.append(current_time)

        # Вызываем следующий handler
        return await handler(event, data)

    def cleanup_old_records(self) -> None:
        """
        Очищает старые записи для экономии памяти.

        Можно вызывать периодически в фоновой задаче.
        """
        current_time = time.time()
        users_to_remove = []

        for user_id, timestamps in self.user_requests.items():
            # Удаляем старые timestamps
            timestamps[:] = [ts for ts in timestamps if current_time - ts < self.per]

            # Если у пользователя не осталось активных timestamps, помечаем на удаление
            if not timestamps:
                users_to_remove.append(user_id)

        # Удаляем пользователей без активных запросов
        for user_id in users_to_remove:
            del self.user_requests[user_id]

        if users_to_remove:
            logger.debug(f"Cleaned up {len(users_to_remove)} users from rate limiter")
