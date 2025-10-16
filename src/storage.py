"""Хранилище истории диалогов в PostgreSQL."""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from src.config import Config
from src.database import Database
from src.models import Message, User, UserSettings

logger = logging.getLogger(__name__)


class Storage:
    """
    Хранилище истории диалогов в PostgreSQL.

    Отвечает за:
    - Загрузку истории диалога из БД
    - Сохранение истории диалога в БД
    - Управление лимитом сообщений (soft delete)
    - Работу с настройками пользователей
    """

    def __init__(self, database: Database, config: Config) -> None:
        """
        Инициализация Storage с Database и конфигурацией.

        Args:
            database: Объект Database для работы с БД
            config: Конфигурация приложения
        """
        self.db = database
        self.config = config

        logger.info("Storage initialized with PostgreSQL backend")

    async def _ensure_user_exists(self, user_id: int) -> None:
        """
        Создаёт пользователя и его настройки, если они не существуют.

        Args:
            user_id: ID пользователя Telegram
        """
        async with self.db.session() as session:
            # Используем INSERT ... ON CONFLICT DO NOTHING для user
            stmt = insert(User).values(id=user_id).on_conflict_do_nothing(index_elements=["id"])
            await session.execute(stmt)

            # Создаём настройки пользователя с дефолтными значениями
            settings_stmt = (
                insert(UserSettings)
                .values(
                    user_id=user_id,
                    max_history_messages=self.config.max_history_messages,
                )
                .on_conflict_do_nothing(index_elements=["user_id"])
            )
            await session.execute(settings_stmt)

        logger.debug(f"User {user_id}: ensured user and settings exist")

    async def _get_user_settings(self, user_id: int) -> UserSettings:
        """
        Получает настройки пользователя из БД.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Объект UserSettings
        """
        await self._ensure_user_exists(user_id)

        async with self.db.session() as session:
            stmt = select(UserSettings).where(UserSettings.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one()

    async def load_history(self, user_id: int) -> list[dict[str, str]]:
        """
        Загружает историю диалога пользователя из БД.

        Возвращает только не удалённые сообщения (soft delete).

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Список сообщений в формате [{"role": "...", "content": "...", "timestamp": "..."}, ...]
            Пустой список, если истории нет
        """
        await self._ensure_user_exists(user_id)

        try:
            async with self.db.session() as session:
                # Загружаем только не удалённые сообщения, отсортированные по времени создания
                stmt = (
                    select(Message)
                    .where(Message.user_id == user_id, Message.deleted_at.is_(None))
                    .order_by(Message.created_at)
                )
                result = await session.execute(stmt)
                messages = result.scalars().all()

                # Конвертируем в формат словарей
                history = [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at.isoformat(),
                    }
                    for msg in messages
                ]

            logger.info(f"User {user_id}: loaded history with {len(history)} messages")
            return history

        except Exception as e:
            logger.error(f"User {user_id}: failed to load history: {e}", exc_info=True)
            return []

    async def save_history(self, user_id: int, messages: list[dict[str, str]]) -> None:
        """
        Сохраняет историю диалога пользователя в БД.

        Автоматически применяет soft delete к старым сообщениям при превышении лимита.
        Всегда сохраняет системный промпт (первое сообщение с role="system").

        Args:
            user_id: ID пользователя Telegram
            messages: Список сообщений для сохранения
        """
        await self._ensure_user_exists(user_id)

        try:
            # Получаем лимит для данного пользователя
            settings = await self._get_user_settings(user_id)
            max_messages = settings.max_history_messages

            async with self.db.session() as session:
                # Получаем текущее количество активных сообщений
                count_stmt = select(Message).where(
                    Message.user_id == user_id, Message.deleted_at.is_(None)
                )
                result = await session.execute(count_stmt)
                current_messages = result.scalars().all()
                current_count = len(current_messages)

                # Вычисляем сколько новых сообщений добавим
                new_messages_count = len(messages) - current_count

                # Если превышаем лимит, помечаем старые сообщения как удалённые (кроме system)
                if current_count + new_messages_count > max_messages:
                    # Сколько сообщений нужно удалить
                    to_delete_count = (current_count + new_messages_count) - max_messages

                    # Получаем самые старые сообщения (исключая system промпт)
                    old_messages_stmt = (
                        select(Message)
                        .where(
                            Message.user_id == user_id,
                            Message.deleted_at.is_(None),
                            Message.role != "system",
                        )
                        .order_by(Message.created_at)
                        .limit(to_delete_count)
                    )
                    old_messages_result = await session.execute(old_messages_stmt)
                    old_messages = old_messages_result.scalars().all()

                    # Soft delete
                    if old_messages:
                        old_message_ids = [msg.id for msg in old_messages]
                        soft_delete_stmt = (
                            update(Message)
                            .where(Message.id.in_(old_message_ids))
                            .values(deleted_at=datetime.now(UTC))
                        )
                        await session.execute(soft_delete_stmt)
                        logger.debug(
                            f"User {user_id}: soft deleted {len(old_messages)} old messages"
                        )

                # Удаляем все текущие сообщения из БД перед вставкой новых
                # (это полное перезаписывание истории при каждом save)
                delete_stmt = delete(Message).where(Message.user_id == user_id)
                await session.execute(delete_stmt)

                # Вставляем все сообщения
                for msg in messages:
                    message = Message(
                        id=uuid4(),
                        user_id=user_id,
                        role=msg["role"],
                        content=msg["content"],
                        content_length=len(msg["content"]),
                        created_at=datetime.fromisoformat(
                            msg.get("timestamp", datetime.now(UTC).isoformat())
                        ),
                    )
                    session.add(message)

            logger.info(f"User {user_id}: saved history with {len(messages)} messages")

        except Exception as e:
            logger.error(f"User {user_id}: failed to save history: {e}", exc_info=True)
            raise

    async def clear_history(self, user_id: int) -> None:
        """
        Очищает историю диалога пользователя (soft delete).

        Помечает все сообщения как удалённые, не удаляя их физически.

        Args:
            user_id: ID пользователя Telegram
        """
        await self._ensure_user_exists(user_id)

        try:
            async with self.db.session() as session:
                # Soft delete всех сообщений пользователя
                stmt = (
                    update(Message)
                    .where(Message.user_id == user_id, Message.deleted_at.is_(None))
                    .values(deleted_at=datetime.now(UTC))
                )
                result = await session.execute(stmt)
                deleted_count = result.rowcount

            logger.info(f"User {user_id}: history cleared ({deleted_count} messages soft deleted)")

        except Exception as e:
            logger.error(f"User {user_id}: failed to clear history: {e}", exc_info=True)
            raise

    async def get_system_prompt(self, user_id: int) -> str | None:
        """
        Получает кастомный системный промпт пользователя из настроек.

        Args:
            user_id: ID пользователя Telegram

        Returns:
            Системный промпт пользователя или None, если используется промпт по умолчанию
        """
        try:
            settings = await self._get_user_settings(user_id)
            system_prompt = settings.system_prompt

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

        Очищает историю сообщений (soft delete) и создаёт новое системное сообщение.

        Args:
            user_id: ID пользователя Telegram
            system_prompt: Новый системный промпт
        """
        await self._ensure_user_exists(user_id)

        try:
            # Очищаем историю (soft delete)
            await self.clear_history(user_id)

            async with self.db.session() as session:
                # Обновляем system_prompt в настройках
                stmt = (
                    update(UserSettings)
                    .where(UserSettings.user_id == user_id)
                    .values(system_prompt=system_prompt, updated_at=datetime.now(UTC))
                )
                await session.execute(stmt)

                # Создаём новое системное сообщение
                system_message = Message(
                    id=uuid4(),
                    user_id=user_id,
                    role="system",
                    content=system_prompt,
                    content_length=len(system_prompt),
                )
                session.add(system_message)

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
        await self._ensure_user_exists(user_id)

        try:
            async with self.db.session() as session:
                # Считаем активные сообщения
                count_stmt = select(Message).where(
                    Message.user_id == user_id, Message.deleted_at.is_(None)
                )
                count_result = await session.execute(count_stmt)
                messages_count = len(count_result.scalars().all())

                # Получаем настройки пользователя
                settings_stmt = select(UserSettings).where(UserSettings.user_id == user_id)
                settings_result = await session.execute(settings_stmt)
                settings = settings_result.scalar_one()

            return {
                "messages_count": messages_count,
                "system_prompt": settings.system_prompt,
                "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
            }

        except Exception as e:
            logger.error(f"User {user_id}: failed to load dialog info: {e}", exc_info=True)
            return {"messages_count": 0, "system_prompt": None, "updated_at": None}
