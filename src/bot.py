"""Основной класс Telegram-бота."""

import logging
from functools import partial

from aiogram import Bot as AiogramBot
from aiogram import Dispatcher
from aiogram.filters import Command

from src.config import Config
from src.database import Database
from src.handlers import commands, messages
from src.llm_client import LLMClient
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
        self._register_handlers()
        logger.info("Bot initialized")

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

    async def stop(self) -> None:
        """Остановка бота и очистка ресурсов."""
        logger.info("Stopping bot...")
        await self.database.close()
        await self.bot.session.close()
        logger.info("Bot stopped")
