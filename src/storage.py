"""Хранилище истории диалогов в JSON файлах."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiofiles

from src.config import Config

logger = logging.getLogger(__name__)


class Storage:
    """
    Хранилище истории диалогов в JSON файлах.

    Отвечает за:
    - Загрузку истории диалога из файла
    - Сохранение истории диалога в файл
    - Управление лимитом сообщений
    - Работу с файловой системой
    """

    def __init__(self, config: Config) -> None:
        """
        Инициализация Storage с конфигурацией.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.data_dir = Path(config.data_dir)

        # Создаём директорию для данных, если её нет
        self.data_dir.mkdir(exist_ok=True)

        logger.info(f"Storage initialized: data_dir={self.data_dir.absolute()}")

    def _get_user_file_path(self, user_id: int) -> Path:
        """
        Получает путь к файлу истории диалога пользователя.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Путь к JSON файлу пользователя
        """
        return self.data_dir / f"{user_id}.json"

    async def load_history(self, user_id: int) -> list[dict[str, str]]:
        """
        Загружает историю диалога пользователя из JSON файла.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений в формате [{"role": "...", "content": "...", "timestamp": "..."}, ...]
            Пустой список, если файла нет или произошла ошибка
        """
        file_path = self._get_user_file_path(user_id)

        # Если файла нет - возвращаем пустую историю
        if not file_path.exists():
            logger.debug(f"User {user_id}: no history file found")
            return []

        try:
            # Читаем файл асинхронно через aiofiles
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)

            messages: list[dict[str, str]] = data.get("messages", [])
            logger.info(f"User {user_id}: loaded history with {len(messages)} messages")
            return messages

        except json.JSONDecodeError as e:
            logger.error(f"User {user_id}: failed to parse JSON from {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(
                f"User {user_id}: failed to load history from {file_path}: {e}", exc_info=True
            )
            return []

    async def save_history(self, user_id: int, messages: list[dict[str, str]]) -> None:
        """
        Сохраняет историю диалога пользователя в JSON файл.

        Автоматически ограничивает количество сообщений до max_history_messages.

        Args:
            user_id: ID пользователя Telegram
            messages: Список сообщений для сохранения
        """
        file_path = self._get_user_file_path(user_id)

        try:
            # Ограничиваем историю
            limited_messages = self._limit_messages(messages)

            # Формируем данные для сохранения
            data = {
                "user_id": user_id,
                "messages": limited_messages,
                "updated_at": datetime.now(UTC).isoformat(),
            }

            # Сохраняем асинхронно через aiofiles
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))

            logger.info(
                f"User {user_id}: saved history with {len(limited_messages)} messages to {file_path}"
            )

        except Exception as e:
            logger.error(
                f"User {user_id}: failed to save history to {file_path}: {e}", exc_info=True
            )
            raise

    def _limit_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Ограничивает количество сообщений в истории.

        Всегда сохраняет первое сообщение (системный промпт) и последние N-1 сообщений.

        Args:
            messages: Список сообщений

        Returns:
            Ограниченный список сообщений
        """
        max_messages = self.config.max_history_messages

        # Если сообщений меньше лимита - возвращаем как есть
        if len(messages) <= max_messages:
            return messages

        # Если первое сообщение - системный промпт, сохраняем его
        if messages and messages[0].get("role") == "system":
            system_prompt = [messages[0]]
            recent_messages = messages[-(max_messages - 1) :]
            result = system_prompt + recent_messages
            logger.debug(
                f"Limited history: kept system prompt + {len(recent_messages)} recent messages"
            )
            return result
        # Если нет системного промпта - просто берём последние N сообщений
        result = messages[-max_messages:]
        logger.debug(f"Limited history: kept {len(result)} recent messages")
        return result

    async def clear_history(self, user_id: int) -> None:
        """
        Очищает историю диалога пользователя.

        Удаляет JSON файл пользователя из файловой системы.

        Args:
            user_id: ID пользователя Telegram
        """
        file_path = self._get_user_file_path(user_id)

        try:
            if file_path.exists():
                # Используем aiofiles для удаления файла
                async with aiofiles.open(file_path):
                    pass  # Просто открываем для проверки доступа
                # Удаляем через Path.unlink (синхронная операция, но быстрая)
                file_path.unlink()
                logger.info(f"User {user_id}: history cleared (file deleted)")
            else:
                logger.debug(f"User {user_id}: no history file to clear")

        except Exception as e:
            logger.error(f"User {user_id}: failed to clear history: {e}", exc_info=True)
            raise

    async def get_system_prompt(self, user_id: int) -> str | None:
        """
        Загружает системный промпт пользователя из файла.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Системный промпт пользователя или None, если используется промпт по умолчанию
        """
        file_path = self._get_user_file_path(user_id)

        if not file_path.exists():
            logger.debug(f"User {user_id}: no file found, no custom system prompt")
            return None

        try:
            # Читаем файл асинхронно через aiofiles
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)

            system_prompt: str | None = data.get("system_prompt")
            if system_prompt:
                logger.debug(
                    f"User {user_id}: loaded custom system prompt ({len(system_prompt)} chars)"
                )
            else:
                logger.debug(f"User {user_id}: using default system prompt")

            return system_prompt

        except Exception as e:
            logger.error(f"User {user_id}: failed to load system prompt: {e}", exc_info=True)
            return None

    async def set_system_prompt(self, user_id: int, system_prompt: str) -> None:
        """
        Устанавливает системный промпт для пользователя.

        Очищает историю сообщений и сохраняет только новый системный промпт.

        Args:
            user_id: ID пользователя Telegram
            system_prompt: Новый системный промпт
        """
        file_path = self._get_user_file_path(user_id)

        try:
            # Создаём новый диалог с системным промптом
            data = {
                "user_id": user_id,
                "system_prompt": system_prompt,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                ],
                "updated_at": datetime.now(UTC).isoformat(),
            }

            # Сохраняем асинхронно через aiofiles
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))

            logger.info(
                f"User {user_id}: system prompt set ({len(system_prompt)} chars), history cleared"
            )

        except Exception as e:
            logger.error(f"User {user_id}: failed to set system prompt: {e}", exc_info=True)
            raise

    async def get_dialog_info(self, user_id: int) -> dict[str, Any]:
        """
        Загружает информацию о диалоге пользователя для отображения статистики.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Словарь с информацией о диалоге:
            - messages_count: количество сообщений в истории
            - system_prompt: текущий системный промпт (или None для default)
            - updated_at: дата последнего обновления (или None)
        """
        file_path = self._get_user_file_path(user_id)

        if not file_path.exists():
            logger.debug(f"User {user_id}: no dialog file found")
            return {"messages_count": 0, "system_prompt": None, "updated_at": None}

        try:
            # Читаем файл асинхронно через aiofiles
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)

            messages = data.get("messages", [])
            system_prompt = data.get("system_prompt")
            updated_at = data.get("updated_at")

            return {
                "messages_count": len(messages),
                "system_prompt": system_prompt,
                "updated_at": updated_at,
            }

        except Exception as e:
            logger.error(f"User {user_id}: failed to load dialog info: {e}", exc_info=True)
            return {"messages_count": 0, "system_prompt": None, "updated_at": None}
