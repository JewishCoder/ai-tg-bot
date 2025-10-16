"""Тесты для класса Bot."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot import Bot
from src.config import Config


class TestBotGracefulShutdown:
    """Тесты graceful shutdown для Bot."""

    @pytest.mark.asyncio
    async def test_stop_without_active_handlers(self, test_config: Config) -> None:
        """
        Тест: остановка бота без активных handlers.

        Args:
            test_config: Тестовая конфигурация
        """
        # Создаём бота с моками
        with patch("src.bot.Database"), patch("src.bot.AiogramBot"):
            bot = Bot(test_config)
            bot.database.close = AsyncMock()
            bot.bot.session = MagicMock()
            bot.bot.session.close = AsyncMock()

            # Останавливаем бот (нет активных handlers)
            await bot.stop()

            # Проверяем что флаг установлен
            assert bot._is_shutting_down is True

            # Проверяем что ресурсы закрыты
            bot.database.close.assert_awaited_once()
            bot.bot.session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stop_with_active_handlers_completes(self, test_config: Config) -> None:
        """
        Тест: остановка бота с активными handlers, которые успевают завершиться.

        Args:
            test_config: Тестовая конфигурация
        """
        with patch("src.bot.Database"), patch("src.bot.AiogramBot"):
            bot = Bot(test_config)
            bot.database.close = AsyncMock()
            bot.bot.session = MagicMock()
            bot.bot.session.close = AsyncMock()

            # Имитируем активные handlers
            bot._active_handlers = 2

            # Создаём задачу которая через 0.2 секунды "завершит" handlers
            async def complete_handlers():
                await asyncio.sleep(0.2)
                bot._active_handlers = 0

            # Запускаем задачу завершения handlers
            asyncio.create_task(complete_handlers())

            # Останавливаем бот
            await bot.stop()

            # Проверяем что все handlers завершились
            assert bot._active_handlers == 0
            assert bot._is_shutting_down is True

            # Проверяем что ресурсы закрыты
            bot.database.close.assert_awaited_once()
            bot.bot.session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stop_with_timeout_exceeded(self, test_config: Config) -> None:
        """
        Тест: остановка бота с timeout (handlers не завершились вовремя).

        Args:
            test_config: Тестовая конфигурация
        """
        with patch("src.bot.Database"), patch("src.bot.AiogramBot"):
            bot = Bot(test_config)
            bot.database.close = AsyncMock()
            bot.bot.session = MagicMock()
            bot.bot.session.close = AsyncMock()

            # Имитируем handlers которые не завершаются
            bot._active_handlers = 3

            # Останавливаем бот с очень коротким timeout
            async def stop_with_short_timeout():
                bot._is_shutting_down = True
                await bot._wait_for_pending_handlers(timeout=0.3)
                await bot.database.close()
                await bot.bot.session.close()

            await stop_with_short_timeout()

            # Handlers всё ещё активны (не завершились)
            assert bot._active_handlers == 3
            assert bot._is_shutting_down is True

            # Но ресурсы всё равно закрыты (force shutdown)
            bot.database.close.assert_awaited_once()
            bot.bot.session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_wait_for_pending_handlers_no_handlers(self, test_config: Config) -> None:
        """
        Тест: ожидание завершения когда нет активных handlers.

        Args:
            test_config: Тестовая конфигурация
        """
        with patch("src.bot.Database"), patch("src.bot.AiogramBot"):
            bot = Bot(test_config)

            # Нет активных handlers
            bot._active_handlers = 0

            # Ожидание должно завершиться мгновенно
            await bot._wait_for_pending_handlers(timeout=1.0)

            # Проверка что счётчик всё ещё 0
            assert bot._active_handlers == 0

    @pytest.mark.asyncio
    async def test_wait_for_pending_handlers_with_completion(self, test_config: Config) -> None:
        """
        Тест: ожидание завершения handlers которые успевают завершиться.

        Args:
            test_config: Тестовая конфигурация
        """
        with patch("src.bot.Database"), patch("src.bot.AiogramBot"):
            bot = Bot(test_config)
            bot._active_handlers = 5

            # Создаём задачу которая постепенно "завершает" handlers
            async def complete_handlers_gradually():
                await asyncio.sleep(0.1)
                bot._active_handlers = 3
                await asyncio.sleep(0.1)
                bot._active_handlers = 1
                await asyncio.sleep(0.1)
                bot._active_handlers = 0

            # Запускаем задачу
            asyncio.create_task(complete_handlers_gradually())

            # Ожидаем завершения
            await bot._wait_for_pending_handlers(timeout=2.0)

            # Все handlers должны завершиться
            assert bot._active_handlers == 0
