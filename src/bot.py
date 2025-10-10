"""Основной класс Telegram-бота."""

import logging
from aiogram import Bot as AiogramBot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.config import Config

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
        self._register_handlers()
        logger.info("Bot initialized")
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        self.dp.message.register(self._handle_start, Command("start"))
        self.dp.message.register(self._handle_help, Command("help"))
        self.dp.message.register(self._handle_echo)
        logger.info("Handlers registered")
    
    async def _handle_start(self, message: Message) -> None:
        """
        Обработчик команды /start.
        
        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id if message.from_user else "unknown"
        logger.info(f"User {user_id}: /start command")
        
        welcome_text = (
            "👋 Привет! Я AI-ассистент на базе LLM.\n\n"
            "Я могу отвечать на твои вопросы и поддерживать диалог.\n"
            "Пока что я работаю в режиме эхо - просто повторяю твои сообщения.\n\n"
            "Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/help - показать список команд\n\n"
            "Просто отправь мне сообщение, и я отвечу!"
        )
        
        await message.answer(welcome_text)
    
    async def _handle_help(self, message: Message) -> None:
        """
        Обработчик команды /help.
        
        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id if message.from_user else "unknown"
        logger.info(f"User {user_id}: /help command")
        
        help_text = (
            "📚 Доступные команды:\n\n"
            "/start - начать работу с ботом\n"
            "/help - показать эту справку\n\n"
            "💬 Просто отправь мне любое текстовое сообщение, и я отвечу!"
        )
        
        await message.answer(help_text)
    
    async def _handle_echo(self, message: Message) -> None:
        """
        Эхо-обработчик для текстовых сообщений.
        
        Отправляет пользователю тот же текст, что получил.
        
        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.text:
            return
        
        user_id = message.from_user.id if message.from_user else "unknown"
        text_length = len(message.text)
        logger.info(f"User {user_id}: received message ({text_length} chars)")
        
        await message.answer(message.text)
        logger.debug(f"User {user_id}: echo response sent")
    
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
        await self.bot.session.close()
        logger.info("Bot stopped")

