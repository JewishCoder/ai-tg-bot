"""Обработчики команд бота."""

import logging
from datetime import datetime

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message

from src.config import Config
from src.storage import Storage

logger = logging.getLogger(__name__)


async def handle_start(message: Message) -> None:
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


async def handle_help(message: Message) -> None:
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


async def handle_role(message: Message, bot: Bot, storage: Storage, config: Config) -> None:
    """
    Обработчик команды /role.

    Устанавливает кастомную роль ассистента или возвращает к роли по умолчанию.

    Использование:
    - /role <текст> - установить кастомную роль
    - /role default - вернуться к роли по умолчанию

    Args:
        message: Входящее сообщение от пользователя
        bot: Экземпляр бота для отправки действий
        storage: Storage для сохранения промпта
        config: Конфигурация с дефолтным промптом
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
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # Проверяем - default или кастомный промпт
        if role_text.lower() == "default":
            system_prompt = config.system_prompt
            await storage.set_system_prompt(user_id, system_prompt)

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
            await storage.set_system_prompt(user_id, role_text)

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


async def handle_status(message: Message, bot: Bot, storage: Storage, config: Config) -> None:
    """
    Обработчик команды /status.

    Показывает статистику диалога:
    - Количество сообщений в истории
    - Текущий системный промпт (первые 100 символов)
    - Дата последнего обновления
    - Используемая модель LLM

    Args:
        message: Входящее сообщение от пользователя
        bot: Экземпляр бота для отправки действий
        storage: Storage для получения информации о диалоге
        config: Конфигурация с настройками модели
    """
    user_id = message.from_user.id if message.from_user else 0
    logger.info(f"User {user_id}: /status command")

    try:
        # Показываем индикатор обработки
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # Получаем информацию о диалоге
        dialog_info = await storage.get_dialog_info(user_id)

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
            prompt_preview = config.system_prompt[:100]
            if len(config.system_prompt) > 100:
                prompt_preview += "..."
            role_type = "🔄 Роль по умолчанию"

        # Форматируем дату
        if updated_at:
            # Парсим ISO формат и форматируем читаемо
            dt = datetime.fromisoformat(updated_at)
            updated_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            updated_str = "Нет данных"

        status_text = (
            f"📊 Статус вашего диалога\n\n"
            f"💬 Сообщений в истории: {messages_count}\n"
            f"🎭 Тип роли: {role_type}\n"
            f"🤖 Модель: {config.openrouter_model}\n"
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


async def handle_reset(message: Message, bot: Bot, storage: Storage, config: Config) -> None:
    """
    Обработчик команды /reset.

    Очищает историю диалога пользователя, сохраняя текущий системный промпт.

    Args:
        message: Входящее сообщение от пользователя
        bot: Экземпляр бота для отправки действий
        storage: Storage для очистки истории
        config: Конфигурация с дефолтным промптом
    """
    user_id = message.from_user.id if message.from_user else 0
    logger.info(f"User {user_id}: /reset command")

    try:
        # Показываем индикатор обработки
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # Получаем текущий системный промпт перед очисткой
        custom_prompt = await storage.get_system_prompt(user_id)

        # Определяем какой промпт использовать
        if custom_prompt:
            system_prompt = custom_prompt
            role_type = "🎭 Кастомная роль"
            role_status = "сохранена"
        else:
            system_prompt = config.system_prompt
            role_type = "🔄 Роль по умолчанию"
            role_status = "сохранена"

        # Устанавливаем промпт заново (это очистит историю)
        await storage.set_system_prompt(user_id, system_prompt)

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
