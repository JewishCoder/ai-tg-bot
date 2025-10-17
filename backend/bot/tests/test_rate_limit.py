"""Тесты для RateLimitMiddleware."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message, User

from src.middlewares.rate_limit import RateLimitMiddleware


class TestRateLimitMiddleware:
    """Тесты для RateLimitMiddleware."""

    @pytest.mark.asyncio
    async def test_middleware_allows_requests_within_limit(self) -> None:
        """
        Тест: middleware пропускает запросы в пределах лимита.
        """
        middleware = RateLimitMiddleware(rate=3, per=60.0, enabled=True)

        # Мокируем handler и message
        handler = AsyncMock(return_value="success")
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.answer = AsyncMock()

        data = {}

        # Делаем 3 запроса (в пределах лимита)
        for _ in range(3):
            result = await middleware(handler, message, data)
            assert result == "success"
            assert handler.call_count == _ + 1

        # Handler должен быть вызван 3 раза
        assert handler.call_count == 3

    @pytest.mark.asyncio
    async def test_middleware_blocks_requests_exceeding_limit(self) -> None:
        """
        Тест: middleware блокирует запросы при превышении лимита.
        """
        middleware = RateLimitMiddleware(rate=2, per=60.0, enabled=True)

        # Мокируем handler и message
        handler = AsyncMock(return_value="success")
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.answer = AsyncMock()

        data = {}

        # Делаем 2 запроса (в пределах лимита)
        for _ in range(2):
            result = await middleware(handler, message, data)
            assert result == "success"

        # 3-й запрос должен быть заблокирован
        result = await middleware(handler, message, data)
        assert result is None

        # Handler должен быть вызван только 2 раза
        assert handler.call_count == 2

        # Проверяем что пользователю было отправлено сообщение
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Слишком много запросов" in call_args

    @pytest.mark.asyncio
    async def test_middleware_disabled(self) -> None:
        """
        Тест: middleware не работает когда отключен.
        """
        middleware = RateLimitMiddleware(rate=1, per=60.0, enabled=False)

        # Мокируем handler и message
        handler = AsyncMock(return_value="success")
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.answer = AsyncMock()

        data = {}

        # Делаем 5 запросов (больше чем лимит, но middleware отключен)
        for _ in range(5):
            result = await middleware(handler, message, data)
            assert result == "success"

        # Handler должен быть вызван 5 раз
        assert handler.call_count == 5

    @pytest.mark.asyncio
    async def test_middleware_clears_old_timestamps(self) -> None:
        """
        Тест: middleware очищает старые timestamps после периода.
        """
        middleware = RateLimitMiddleware(rate=2, per=1.0, enabled=True)

        # Мокируем handler и message
        handler = AsyncMock(return_value="success")
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 12345
        message.answer = AsyncMock()

        data = {}

        # Делаем 2 запроса (заполняем лимит)
        for _ in range(2):
            await middleware(handler, message, data)

        assert handler.call_count == 2

        # 3-й запрос блокируется
        result = await middleware(handler, message, data)
        assert result is None
        assert handler.call_count == 2

        # Ждём 1.1 секунды (период + запас)
        time.sleep(1.1)

        # После периода timestamps должны очиститься, и запрос должен пройти
        result = await middleware(handler, message, data)
        assert result == "success"
        assert handler.call_count == 3

    @pytest.mark.asyncio
    async def test_middleware_different_users_independent_limits(self) -> None:
        """
        Тест: лимиты для разных пользователей независимы.
        """
        middleware = RateLimitMiddleware(rate=2, per=60.0, enabled=True)

        # Мокируем handler
        handler = AsyncMock(return_value="success")

        # Два разных пользователя
        message1 = MagicMock(spec=Message)
        message1.from_user = MagicMock(spec=User)
        message1.from_user.id = 11111
        message1.answer = AsyncMock()

        message2 = MagicMock(spec=Message)
        message2.from_user = MagicMock(spec=User)
        message2.from_user.id = 22222
        message2.answer = AsyncMock()

        data = {}

        # Пользователь 1: 2 запроса
        for _ in range(2):
            result = await middleware(handler, message1, data)
            assert result == "success"

        # Пользователь 2: 2 запроса (должны пройти независимо)
        for _ in range(2):
            result = await middleware(handler, message2, data)
            assert result == "success"

        # Оба пользователя сделали по 2 запроса
        assert handler.call_count == 4

        # Пользователь 1: 3-й запрос блокируется
        result = await middleware(handler, message1, data)
        assert result is None

        # Пользователь 2: 3-й запрос блокируется
        result = await middleware(handler, message2, data)
        assert result is None

        # Handler всё ещё вызван 4 раза
        assert handler.call_count == 4

    @pytest.mark.asyncio
    async def test_middleware_skips_messages_without_user(self) -> None:
        """
        Тест: middleware пропускает сообщения без user_id.
        """
        middleware = RateLimitMiddleware(rate=1, per=60.0, enabled=True)

        # Мокируем handler и message без user
        handler = AsyncMock(return_value="success")
        message = MagicMock(spec=Message)
        message.from_user = None

        data = {}

        # Запрос должен пройти несмотря на отсутствие user_id
        result = await middleware(handler, message, data)
        assert result == "success"
        assert handler.call_count == 1

    def test_cleanup_old_records(self) -> None:
        """
        Тест: метод cleanup_old_records очищает старые записи.
        """
        middleware = RateLimitMiddleware(rate=5, per=1.0, enabled=True)

        # Добавляем запросы для нескольких пользователей
        current_time = time.time()
        middleware.user_requests[11111] = [current_time - 2.0, current_time - 1.5]  # Старые
        middleware.user_requests[22222] = [current_time - 0.5, current_time]  # Свежие
        middleware.user_requests[33333] = [current_time - 5.0]  # Очень старые

        # Вызываем cleanup
        middleware.cleanup_old_records()

        # Пользователь 11111 и 33333 должны быть удалены (все timestamps старые)
        assert 11111 not in middleware.user_requests
        assert 33333 not in middleware.user_requests

        # Пользователь 22222 должен остаться
        assert 22222 in middleware.user_requests
        assert len(middleware.user_requests[22222]) == 2
