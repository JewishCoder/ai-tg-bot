"""Обработчик текстовых сообщений."""

import asyncio
import logging
from datetime import UTC, datetime

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message

from src.config import Config
from src.llm_client import LLMAPIError, LLMClient
from src.storage import Storage
from src.utils.error_formatter import get_error_message
from src.utils.message_splitter import split_message

logger = logging.getLogger(__name__)


async def handle_message(
    message: Message,
    bot: Bot,
    llm_client: LLMClient,
    storage: Storage,
    config: Config,
) -> None:
    """
    Обработчик текстовых сообщений пользователя.

    Загружает историю диалога, отправляет в LLM и сохраняет обновленную историю.

    Args:
        message: Входящее сообщение от пользователя
        bot: Экземпляр бота для отправки действий
        llm_client: Клиент для работы с LLM
        storage: Storage для загрузки/сохранения истории
        config: Конфигурация с системным промптом
    """
    if not message.text:
        return

    user_id = message.from_user.id if message.from_user else 0
    text_length = len(message.text)
    logger.info(f"User {user_id}: received message ({text_length} chars)")

    try:
        # Показываем индикатор "печатает..."
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        # 1. Загружаем последние N сообщений (для оптимизации контекста LLM)
        history = await storage.load_recent_history(user_id, limit=config.max_context_messages)

        # 2. Если истории нет - инициализируем новый диалог с системным промптом
        if not history:
            # Загружаем кастомный промпт (если есть) или используем default
            custom_prompt = await storage.get_system_prompt(user_id)
            system_prompt = custom_prompt if custom_prompt else config.system_prompt

            # Создаём новый диалог с системным промптом
            history = [
                {
                    "role": "system",
                    "content": system_prompt,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ]

            # Сохраняем системный промпт в Storage для нового пользователя
            if not custom_prompt:
                await storage.set_system_prompt(user_id, system_prompt)

            logger.debug(
                f"User {user_id}: initialized new dialog with "
                f"{'custom' if custom_prompt else 'default'} system prompt"
            )

        # 3. Добавляем сообщение пользователя
        history.append(
            {
                "role": "user",
                "content": message.text,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # 4. Получаем ответ от LLM
        response = await llm_client.generate_response(messages=history, user_id=user_id)

        # 5. Добавляем ответ ассистента в историю
        history.append(
            {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # 6. Сохраняем обновленную историю
        await storage.save_history(user_id, history)

        # 7. Отправляем ответ пользователю (с разбивкой если нужно)
        # Разбиваем длинные сообщения на части
        message_parts = split_message(response)

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
                # Добавляем индикатор части
                part_indicator = f"📄 Часть {i}/{len(message_parts)}\n\n"
                part_with_indicator = part_indicator + part

                await message.answer(part_with_indicator)

                # Небольшая задержка между частями для лучшей читаемости
                if i < len(message_parts):
                    await asyncio.sleep(0.5)

            logger.debug(f"User {user_id}: all {len(message_parts)} parts sent successfully")

    except LLMAPIError as e:
        logger.error(f"User {user_id}: LLM API error: {e}")

        # Отправляем понятное сообщение об ошибке
        error_message = get_error_message(str(e))
        await message.answer(error_message)

    except Exception as e:
        logger.error(f"User {user_id}: Unexpected error: {e}", exc_info=True)
        await message.answer("⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.")
