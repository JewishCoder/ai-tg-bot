"""Основной класс Telegram-бота."""

import asyncio
import logging
from functools import partial

from aiogram import Bot as AiogramBot
from aiogram import Dispatcher
from aiogram.filters import Command

from src.config import Config
from src.database import Database
from src.handlers import commands, messages
from src.llm_client import LLMClient
from src.middlewares import RateLimitMiddleware
from src.storage import Storage

logger = logging.getLogger(__name__)


class Bot:
    """
    Основной класс Telegram-бота.

    Отвечает за:
    - Инициализацию aiogram Bot и Dispatcher
    - Регистрацию обработчиков команд и сообщений
    - Запуск polling
    """

    def __init__(self, config: Config) -> None:
        """
        Инициализация бота с конфигурацией.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.bot = AiogramBot(token=config.telegram_token)
        self.dp = Dispatcher()
        self.database = Database(config)
        self.llm_client = LLMClient(config)
        self.storage = Storage(self.database, config)
        self._is_shutting_down = False
        self._active_handlers = 0
        self._register_middlewares()
        self._register_handlers()
        logger.info("Bot initialized")

    def _register_middlewares(self) -> None:
        """Регистрация middleware."""
        # Rate limiting middleware
        rate_limiter = RateLimitMiddleware(
            rate=self.config.rate_limit_requests,
            per=self.config.rate_limit_period,
            enabled=self.config.rate_limit_enabled,
        )
        self.dp.message.middleware(rate_limiter)
        logger.info("Middlewares registered")

    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        # Команды без зависимостей
        self.dp.message.register(commands.handle_start, Command("start"))
        self.dp.message.register(commands.handle_help, Command("help"))

        # Команды с зависимостями (используем partial для передачи аргументов)
        self.dp.message.register(
            partial(
                commands.handle_role,
                bot=self.bot,
                storage=self.storage,
                config=self.config,
            ),
            Command("role"),
        )
        self.dp.message.register(
            partial(
                commands.handle_status,
                bot=self.bot,
                storage=self.storage,
                config=self.config,
            ),
            Command("status"),
        )
        self.dp.message.register(
            partial(
                commands.handle_reset,
                bot=self.bot,
                storage=self.storage,
                config=self.config,
            ),
            Command("reset"),
        )

        # Обработчик текстовых сообщений
        self.dp.message.register(
            partial(
                messages.handle_message,
                bot=self.bot,
                llm_client=self.llm_client,
                storage=self.storage,
                config=self.config,
            )
        )

        logger.info("Handlers registered")

    async def start(self) -> None:
        """Запуск бота в режиме polling."""
        logger.info("Starting bot polling...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error during polling: {e}", exc_info=True)
            raise

    async def _wait_for_pending_handlers(self, timeout: float = 30.0) -> None:
        """
        Ожидание завершения активных handlers с timeout.

        Args:
            timeout: Максимальное время ожидания в секундах
        """
        if self._active_handlers == 0:
            logger.info("No active handlers to wait for")
            return

        logger.info(f"Waiting for {self._active_handlers} active handlers to complete...")

        start_time = asyncio.get_event_loop().time()

        while self._active_handlers > 0:
            # Проверяем timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                logger.warning(
                    f"Graceful shutdown timeout after {timeout}s. "
                    f"{self._active_handlers} handlers still active"
                )
                break

            # Ждём немного перед следующей проверкой
            await asyncio.sleep(0.1)

        if self._active_handlers == 0:
            logger.info("All handlers completed successfully")

    async def stop(self) -> None:
        """
        Остановка бота с graceful shutdown.

        Ожидает завершения активных handlers с timeout 30 секунд,
        затем закрывает ресурсы (БД, HTTP сессии).
        """
        logger.info("Initiating graceful shutdown...")

        # Устанавливаем флаг остановки
        self._is_shutting_down = True

        # Ждём завершения активных handlers
        await self._wait_for_pending_handlers(timeout=30.0)

        # Закрываем ресурсы
        logger.info("Closing database connection...")
        await self.database.close()

        logger.info("Closing bot session...")
        await self.bot.session.close()

        logger.info("Bot stopped gracefully")
