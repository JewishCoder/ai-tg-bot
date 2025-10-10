"""Основной класс Telegram-бота."""

import asyncio
import logging
from datetime import datetime
from aiogram import Bot as AiogramBot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatAction

from src.config import Config
from src.llm_client import LLMClient, LLMAPIError
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
        self.llm_client = LLMClient(config)
        self.storage = Storage(config)
        self._register_handlers()
        logger.info("Bot initialized")
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений."""
        self.dp.message.register(self._handle_start, Command("start"))
        self.dp.message.register(self._handle_help, Command("help"))
        self.dp.message.register(self._handle_role, Command("role"))
        self.dp.message.register(self._handle_status, Command("status"))
        self.dp.message.register(self._handle_reset, Command("reset"))
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
            "Я запоминаю контекст разговора, чтобы давать более точные ответы!\n\n"
            "Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/help - показать список команд\n"
            "/role <промпт> - установить роль ассистента\n"
            "/role default - вернуться к роли по умолчанию\n"
            "/status - показать статус и статистику\n"
            "/reset - очистить историю диалога\n\n"
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
            "/help - показать эту справку\n"
            "/role <промпт> - установить роль ассистента\n"
            "/role default - вернуться к роли по умолчанию\n"
            "/status - показать статус и статистику\n"
            "/reset - очистить историю диалога\n\n"
            "💬 Просто отправь мне любое текстовое сообщение, и я отвечу!\n"
            "Я запоминаю контекст разговора для более точных ответов."
        )
        
        await message.answer(help_text)
    
    async def _handle_role(self, message: Message) -> None:
        """
        Обработчик команды /role.
        
        Устанавливает кастомную роль ассистента или возвращает к роли по умолчанию.
        
        Использование:
        - /role <текст> - установить кастомную роль
        - /role default - вернуться к роли по умолчанию
        
        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id if message.from_user else 0
        logger.info(f"User {user_id}: /role command")
        
        # Извлекаем аргументы команды
        if not message.text:
            await message.answer(
                "❌ Неправильное использование команды!\n\n"
                "Используйте:\n"
                "• /role <текст> — установить кастомную роль\n"
                "• /role default — вернуться к роли по умолчанию\n\n"
                "Пример:\n"
                "/role Ты опытный Python разработчик. Помогаешь с кодом и архитектурой."
            )
            return
        
        # Убираем команду из текста
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            await message.answer(
                "❌ Неправильное использование команды!\n\n"
                "Используйте:\n"
                "• /role <текст> — установить кастомную роль\n"
                "• /role default — вернуться к роли по умолчанию\n\n"
                "Пример:\n"
                "/role Ты опытный Python разработчик. Помогаешь с кодом и архитектурой."
            )
            return
        
        role_text = args[1].strip()
        
        try:
            # Показываем индикатор обработки
            await self.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )
            
            # Проверяем - default или кастомный промпт
            if role_text.lower() == "default":
                system_prompt = self.config.system_prompt
                await self.storage.set_system_prompt(user_id, system_prompt)
                
                # Показываем первые 100 символов
                prompt_preview = system_prompt[:100]
                if len(system_prompt) > 100:
                    prompt_preview += "..."
                
                await message.answer(
                    "✅ Роль успешно изменена!\n\n"
                    "🔄 Установлена роль по умолчанию\n"
                    "🗑️ История диалога очищена\n\n"
                    f"📝 Новая роль:\n{prompt_preview}"
                )
                logger.info(f"User {user_id}: role reset to default")
            else:
                # Устанавливаем кастомный промпт
                await self.storage.set_system_prompt(user_id, role_text)
                
                # Показываем первые 100 символов
                prompt_preview = role_text[:100]
                if len(role_text) > 100:
                    prompt_preview += "..."
                
                await message.answer(
                    "✅ Роль успешно изменена!\n\n"
                    "🎭 Установлена кастомная роль\n"
                    "🗑️ История диалога очищена\n\n"
                    f"📝 Новая роль:\n{prompt_preview}"
                )
                logger.info(f"User {user_id}: custom role set ({len(role_text)} chars)")
            
        except Exception as e:
            logger.error(f"User {user_id}: Failed to set role: {e}", exc_info=True)
            await message.answer(
                "❌ Не удалось изменить роль!\n\n"
                "⚠️ Произошла ошибка при сохранении. Попробуйте позже или обратитесь к администратору."
            )
    
    async def _handle_status(self, message: Message) -> None:
        """
        Обработчик команды /status.
        
        Показывает статистику диалога:
        - Количество сообщений в истории
        - Текущий системный промпт (первые 100 символов)
        - Дата последнего обновления
        - Используемая модель LLM
        
        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id if message.from_user else 0
        logger.info(f"User {user_id}: /status command")
        
        try:
            # Показываем индикатор обработки
            await self.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )
            
            # Получаем информацию о диалоге
            dialog_info = await self.storage.get_dialog_info(user_id)
            
            messages_count = dialog_info["messages_count"]
            system_prompt = dialog_info["system_prompt"]
            updated_at = dialog_info["updated_at"]
            
            # Определяем текущий системный промпт
            if system_prompt:
                prompt_preview = system_prompt[:100]
                if len(system_prompt) > 100:
                    prompt_preview += "..."
                role_type = "🎭 Кастомная роль"
            else:
                prompt_preview = self.config.system_prompt[:100]
                if len(self.config.system_prompt) > 100:
                    prompt_preview += "..."
                role_type = "🔄 Роль по умолчанию"
            
            # Форматируем дату
            if updated_at:
                # Парсим ISO формат и форматируем читаемо
                from datetime import datetime
                dt = datetime.fromisoformat(updated_at)
                updated_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                updated_str = "Нет данных"
            
            status_text = (
                f"📊 Статус вашего диалога\n\n"
                f"💬 Сообщений в истории: {messages_count}\n"
                f"🎭 Тип роли: {role_type}\n"
                f"🤖 Модель: {self.config.openrouter_model}\n"
                f"📅 Последнее обновление: {updated_str}\n\n"
                f"📝 Текущая роль:\n{prompt_preview}"
            )
            
            await message.answer(status_text)
            logger.info(f"User {user_id}: status sent")
            
        except Exception as e:
            logger.error(f"User {user_id}: Failed to get status: {e}", exc_info=True)
            await message.answer(
                "❌ Не удалось получить статус!\n\n"
                "⚠️ Произошла ошибка при загрузке данных. Попробуйте позже."
            )
    
    async def _handle_reset(self, message: Message) -> None:
        """
        Обработчик команды /reset.
        
        Очищает историю диалога пользователя, сохраняя текущий системный промпт.
        
        Args:
            message: Входящее сообщение от пользователя
        """
        user_id = message.from_user.id if message.from_user else 0
        logger.info(f"User {user_id}: /reset command")
        
        try:
            # Показываем индикатор обработки
            await self.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )
            
            # Получаем текущий системный промпт перед очисткой
            custom_prompt = await self.storage.get_system_prompt(user_id)
            
            # Определяем какой промпт использовать
            if custom_prompt:
                system_prompt = custom_prompt
                role_type = "🎭 Кастомная роль"
                role_status = "сохранена"
            else:
                system_prompt = self.config.system_prompt
                role_type = "🔄 Роль по умолчанию"
                role_status = "сохранена"
            
            # Устанавливаем промпт заново (это очистит историю)
            await self.storage.set_system_prompt(user_id, system_prompt)
            
            await message.answer(
                "✅ История успешно очищена!\n\n"
                f"🗑️ Все сообщения удалены\n"
                f"{role_type} {role_status}\n\n"
                "Начинаем диалог с чистого листа!"
            )
            logger.info(f"User {user_id}: history reset, role preserved")
            
        except Exception as e:
            logger.error(f"User {user_id}: Failed to reset history: {e}", exc_info=True)
            await message.answer(
                "❌ Не удалось очистить историю!\n\n"
                "⚠️ Произошла ошибка при сохранении. Попробуйте позже."
            )
    
    async def _handle_message(self, message: Message) -> None:
        """
        Обработчик текстовых сообщений.
        
        Загружает историю диалога, отправляет в LLM и сохраняет обновленную историю.
        
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
            
            # 1. Загружаем историю диалога
            history = await self.storage.load_history(user_id)
            
            # 2. Если истории нет - инициализируем новый диалог с системным промптом
            if not history:
                # Загружаем кастомный промпт (если есть) или используем default
                custom_prompt = await self.storage.get_system_prompt(user_id)
                system_prompt = custom_prompt if custom_prompt else self.config.system_prompt
                
                # Создаём новый диалог с системным промптом
                history = [{
                    "role": "system",
                    "content": system_prompt,
                    "timestamp": datetime.now().isoformat()
                }]
                
                # Сохраняем системный промпт в Storage для нового пользователя
                if not custom_prompt:
                    await self.storage.set_system_prompt(user_id, system_prompt)
                
                logger.debug(
                    f"User {user_id}: initialized new dialog with "
                    f"{'custom' if custom_prompt else 'default'} system prompt"
                )
            
            # 3. Добавляем сообщение пользователя
            history.append({
                "role": "user",
                "content": message.text,
                "timestamp": datetime.now().isoformat()
            })
            
            # 4. Получаем ответ от LLM
            response = await self.llm_client.generate_response(
                messages=history,
                user_id=user_id
            )
            
            # 5. Добавляем ответ ассистента в историю
            history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 6. Сохраняем обновленную историю
            await self.storage.save_history(user_id, history)
            
            # 7. Отправляем ответ пользователю (с разбивкой если нужно)
            # Разбиваем длинные сообщения на части
            message_parts = self._split_message(response)
            
            if len(message_parts) == 1:
                # Короткое сообщение - отправляем как есть
                await message.answer(response)
                logger.debug(f"User {user_id}: response sent ({len(response)} chars)")
            else:
                # Длинное сообщение - отправляем по частям
                logger.info(
                    f"User {user_id}: splitting long response into {len(message_parts)} parts "
                    f"(total {len(response)} chars)"
                )
                
                for i, part in enumerate(message_parts, 1):
                    # Добавляем индикатор части если сообщений больше одного
                    if len(message_parts) > 1:
                        part_indicator = f"📄 Часть {i}/{len(message_parts)}\n\n"
                        part_with_indicator = part_indicator + part
                    else:
                        part_with_indicator = part
                    
                    await message.answer(part_with_indicator)
                    
                    # Небольшая задержка между частями для лучшей читаемости
                    if i < len(message_parts):
                        await asyncio.sleep(0.5)
                
                logger.debug(
                    f"User {user_id}: all {len(message_parts)} parts sent successfully"
                )
            
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
    
    def _split_message(self, text: str, max_length: int = 4096) -> list[str]:
        """
        Разбивает длинный текст на части, не превышающие max_length символов.
        
        Старается разбивать по границам абзацев и предложений для читаемости.
        
        Args:
            text: Текст для разбивки
            max_length: Максимальная длина одной части (по умолчанию 4096)
            
        Returns:
            Список частей текста
        """
        # Если текст короче лимита, возвращаем как есть
        if len(text) <= max_length:
            return [text]
        
        parts = []
        remaining_text = text
        
        while remaining_text:
            # Если остаток меньше лимита, добавляем и выходим
            if len(remaining_text) <= max_length:
                parts.append(remaining_text)
                break
            
            # Ищем место для разрыва
            chunk = remaining_text[:max_length]
            
            # Пытаемся разбить по двойному переводу строки (абзацы)
            split_pos = chunk.rfind("\n\n")
            
            # Если не нашли, пытаемся по одинарному переводу строки
            if split_pos == -1:
                split_pos = chunk.rfind("\n")
            
            # Если не нашли, пытаемся по точке с пробелом (конец предложения)
            if split_pos == -1:
                split_pos = chunk.rfind(". ")
                if split_pos != -1:
                    split_pos += 1  # Включаем точку в текущую часть
            
            # Если не нашли, пытаемся по любому пробелу
            if split_pos == -1:
                split_pos = chunk.rfind(" ")
            
            # В крайнем случае режем по лимиту (оставляем небольшой margin)
            if split_pos == -1 or split_pos < max_length * 0.5:
                split_pos = max_length - 100  # Оставляем margin для безопасности
            
            # Добавляем часть и продолжаем с остатком
            parts.append(remaining_text[:split_pos].strip())
            remaining_text = remaining_text[split_pos:].strip()
        
        return parts
    
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

