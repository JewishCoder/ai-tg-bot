"""Хранилище истории диалогов в JSON файлах."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any

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
            # Читаем файл асинхронно через asyncio
            import asyncio
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._read_json_file, file_path)
            
            messages = data.get("messages", [])
            logger.info(f"User {user_id}: loaded history with {len(messages)} messages")
            return messages
            
        except json.JSONDecodeError as e:
            logger.error(f"User {user_id}: failed to parse JSON from {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"User {user_id}: failed to load history from {file_path}: {e}", exc_info=True)
            return []
    
    def _read_json_file(self, file_path: Path) -> dict[str, Any]:
        """
        Синхронное чтение JSON файла.
        
        Args:
            file_path: Путь к JSON файлу
            
        Returns:
            Данные из JSON файла
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    async def save_history(
        self, 
        user_id: int, 
        messages: list[dict[str, str]]
    ) -> None:
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
                "updated_at": datetime.now().isoformat()
            }
            
            # Сохраняем асинхронно
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_json_file, file_path, data)
            
            logger.info(
                f"User {user_id}: saved history with {len(limited_messages)} messages to {file_path}"
            )
            
        except Exception as e:
            logger.error(
                f"User {user_id}: failed to save history to {file_path}: {e}",
                exc_info=True
            )
            raise
    
    def _write_json_file(self, file_path: Path, data: dict[str, Any]) -> None:
        """
        Синхронная запись JSON файла.
        
        Args:
            file_path: Путь к JSON файлу
            data: Данные для записи
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
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
            recent_messages = messages[-(max_messages - 1):]
            result = system_prompt + recent_messages
            logger.debug(
                f"Limited history: kept system prompt + {len(recent_messages)} recent messages"
            )
            return result
        else:
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
                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, file_path.unlink)
                logger.info(f"User {user_id}: history cleared (file deleted)")
            else:
                logger.debug(f"User {user_id}: no history file to clear")
                
        except Exception as e:
            logger.error(
                f"User {user_id}: failed to clear history: {e}",
                exc_info=True
            )
            raise

