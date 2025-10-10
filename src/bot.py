"""Основной класс Telegram-бота."""

import logging
from aiogram import Bot as AiogramBot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatAction

from src.config import Config
from src.llm_client import LLMClient, LLMAPIError

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
        self.llm_client = LLMClient(config)
        self._register_handlers()
        logger.info("Bot initialized")
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        self.dp.message.register(self._handle_start, Command("start"))
        self.dp.message.register(self._handle_help, Command("help"))
        self.dp.message.register(self._handle_message)
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
            "Задавай любые вопросы, и я постараюсь помочь!\n\n"
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
    
    async def _handle_message(self, message: Message) -> None:
        """
        Обработчик текстовых сообщений.
        
        Отправляет сообщение в LLM и возвращает ответ пользователю.
        
        Args:
            message: Входящее сообщение от пользователя
        """
        if not message.text:
            return
        
        user_id = message.from_user.id if message.from_user else 0
        text_length = len(message.text)
        logger.info(f"User {user_id}: received message ({text_length} chars)")
        
        try:
            # Показываем индикатор "печатает..."
            await self.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )
            
            # Получаем ответ от LLM
            response = await self.llm_client.generate_response(
                user_message=message.text,
                user_id=user_id
            )
            
            # Отправляем ответ пользователю
            await message.answer(response)
            logger.debug(f"User {user_id}: LLM response sent ({len(response)} chars)")
            
        except LLMAPIError as e:
            logger.error(f"User {user_id}: LLM API error: {e}")
            
            # Отправляем понятное сообщение об ошибке
            error_message = self._get_error_message(str(e))
            await message.answer(error_message)
            
        except Exception as e:
            logger.error(f"User {user_id}: Unexpected error: {e}", exc_info=True)
            await message.answer(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
    
    def _get_error_message(self, error: str) -> str:
        """
        Получает понятное пользователю сообщение об ошибке.
        
        Args:
            error: Текст ошибки
            
        Returns:
            Сообщение для пользователя
        """
        error_lower = error.lower()
        
        if "rate limit" in error_lower:
            return "⏳ Превышен лимит запросов. Попробуйте через минуту."
        elif "timeout" in error_lower:
            return "⏱️ Запрос к LLM занял слишком много времени. Попробуйте ещё раз."
        elif "connection" in error_lower:
            return "🔌 Проблема с подключением к LLM. Попробуйте позже."
        else:
            return "❌ Не удалось получить ответ от LLM. Попробуйте позже."
    
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

