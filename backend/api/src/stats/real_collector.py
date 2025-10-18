"""Real реализация сборщика статистики с подключением к PostgreSQL."""

import logging
from datetime import UTC, datetime, timedelta

from cachetools import TTLCache
from sqlalchemy import Integer, func, select
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.database import Database
from src.models import Message, User

from .collector import PeriodType, StatCollector
from .models import ActivityPoint, RecentDialog, StatsResponse, Summary, TopUser

logger = logging.getLogger(__name__)


class RealStatCollector(StatCollector):
    """
    Real реализация сборщика статистики из PostgreSQL.

    Получает данные из таблиц бота: users, messages, user_settings.
    Использует агрегированные SQL запросы для производительности.
    """

    def __init__(self, database: Database, cache_ttl: int = 60, cache_maxsize: int = 100) -> None:
        """
        Инициализация Real collector с кешированием.

        Args:
            database: Database объект для работы с PostgreSQL
            cache_ttl: Время жизни кеша в секундах (default: 60)
            cache_maxsize: Максимальный размер кеша (default: 100)
        """
        self.db = database
        self.cache: TTLCache[str, StatsResponse] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        logger.info(
            f"RealStatCollector initialized with PostgreSQL backend "
            f"(cache: TTL={cache_ttl}s, maxsize={cache_maxsize})"
        )

    async def get_stats(self, period: PeriodType) -> StatsResponse:
        """
        Получить статистику за указанный период из БД с кешированием.

        Использует TTL cache для уменьшения нагрузки на БД.
        Cache key = "stats:{period}"

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с реальными данными из БД или из кеша

        Raises:
            ValueError: Если period невалиден
            Exception: При ошибке получения данных из БД
        """
        if period not in ("day", "week", "month"):
            raise ValueError(f"Invalid period: {period}. Must be 'day', 'week' or 'month'")

        # Проверяем кеш
        cache_key = f"stats:{period}"
        if cache_key in self.cache:
            logger.debug(f"Cache HIT for {cache_key}")
            return self.cache[cache_key]

        logger.info(f"Cache MISS for {cache_key}, fetching from DB (period={period})")

        # Fetch с retry механизмом
        response = await self._fetch_stats_from_db(period)

        # Сохраняем в кеш
        self.cache[cache_key] = response
        logger.debug(f"Cached response for {cache_key}")

        return response

    @retry(
        retry=retry_if_exception_type((OperationalError, DBAPIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _fetch_stats_from_db(self, period: PeriodType) -> StatsResponse:
        """
        Внутренний метод для запроса к БД с retry механизмом.

        Retry логика:
        - Количество попыток: 3
        - Exponential backoff: 1s, 2s, 4s
        - Retry только для OperationalError и DBAPIError

        Args:
            period: Период для статистики

        Returns:
            StatsResponse с данными из БД

        Raises:
            OperationalError: При ошибке подключения к БД
            DBAPIError: При ошибке выполнения SQL запросов
        """
        # Определяем временной диапазон
        time_range = self._get_time_range(period)

        async with self.db.session() as session:
            # Параллельный запрос всех данных
            summary = await self._get_summary(session, time_range)
            activity_timeline = await self._get_activity_timeline(session, period, time_range)
            recent_dialogs = await self._get_recent_dialogs(session, time_range)
            top_users = await self._get_top_users(session, time_range)

        return StatsResponse(
            summary=summary,
            activity_timeline=activity_timeline,
            recent_dialogs=recent_dialogs,
            top_users=top_users,
        )

    def _get_time_range(self, period: PeriodType) -> tuple[datetime, datetime]:
        """
        Вычисляет временной диапазон для периода.

        Args:
            period: Период ('day', 'week', 'month')

        Returns:
            Tuple (start_time, end_time) в UTC
        """
        now = datetime.now(UTC)

        if period == "day":
            start_time = now - timedelta(days=1)
        elif period == "week":
            start_time = now - timedelta(weeks=1)
        else:  # month
            start_time = now - timedelta(days=30)

        return start_time, now

    async def _get_summary(
        self, session: AsyncSession, time_range: tuple[datetime, datetime]
    ) -> Summary:
        """
        Получить общую статистику за период.

        Бизнес-логика:
        - total_users: COUNT(DISTINCT users.id) за весь период
        - total_messages: COUNT(messages) WHERE deleted_at IS NULL
        - active_dialogs: COUNT(DISTINCT messages.user_id) WHERE deleted_at IS NULL

        Args:
            session: AsyncSession для запросов
            time_range: Tuple (start_time, end_time)

        Returns:
            Summary с агрегированными данными
        """
        start_time, end_time = time_range

        # Запрос для total_users (всего пользователей)
        total_users_stmt = select(func.count(func.distinct(User.id))).where(
            User.created_at <= end_time
        )
        total_users_result = await session.execute(total_users_stmt)
        total_users = total_users_result.scalar_one()

        # Запрос для total_messages и active_dialogs
        # Оптимизация: одним запросом получаем оба значения
        stats_stmt = select(
            func.count(Message.id).label("total_messages"),
            func.count(func.distinct(Message.user_id)).label("active_dialogs"),
        ).where(
            Message.created_at >= start_time,
            Message.created_at <= end_time,
            Message.deleted_at.is_(None),  # Только не удаленные (soft delete)
        )
        stats_result = await session.execute(stats_stmt)
        stats_row = stats_result.one()

        logger.debug(
            f"Summary: users={total_users}, messages={stats_row.total_messages}, "
            f"dialogs={stats_row.active_dialogs}"
        )

        return Summary(
            total_users=total_users,
            total_messages=stats_row.total_messages,
            active_dialogs=stats_row.active_dialogs,
        )

    async def _get_activity_timeline(
        self, session: AsyncSession, period: PeriodType, time_range: tuple[datetime, datetime]
    ) -> list[ActivityPoint]:
        """
        Получить timeline активности с группировкой по времени.

        Бизнес-логика:
        - day: 24 точки (почасовая агрегация за последние 24 часа)
        - week: 7 точек (дневная агрегация за последние 7 дней)
        - month: 30 точек (дневная агрегация за последние 30 дней)

        Args:
            session: AsyncSession для запросов
            period: Период ('day', 'week', 'month')
            time_range: Tuple (start_time, end_time)

        Returns:
            Список ActivityPoint, отсортированный по timestamp ASC
        """
        start_time, end_time = time_range

        # Определяем функцию группировки по периоду
        if period == "day":
            # Группировка по часам: date_trunc('hour', created_at)
            time_bucket = func.date_trunc("hour", Message.created_at)
        else:  # week, month
            # Группировка по дням: date_trunc('day', created_at)
            time_bucket = func.date_trunc("day", Message.created_at)

        # Агрегированный запрос
        stmt = (
            select(
                time_bucket.label("timestamp"),
                func.count(Message.id).label("message_count"),
                func.count(func.distinct(Message.user_id)).label("active_users"),
            )
            .where(
                Message.created_at >= start_time,
                Message.created_at <= end_time,
                Message.deleted_at.is_(None),  # Только не удаленные
            )
            .group_by("timestamp")
            .order_by("timestamp")
        )

        result = await session.execute(stmt)
        rows = result.all()

        # Преобразуем в список ActivityPoint
        activity_points = [
            ActivityPoint(
                timestamp=row.timestamp,
                message_count=row.message_count,
                active_users=row.active_users,
            )
            for row in rows
        ]

        logger.debug(f"Activity timeline: {len(activity_points)} points for period={period}")

        return activity_points

    async def _get_recent_dialogs(
        self, session: AsyncSession, time_range: tuple[datetime, datetime]
    ) -> list[RecentDialog]:
        """
        Получить последние 10-15 диалогов.

        Бизнес-логика:
        - Группировка по user_id
        - last_message_at: MAX(created_at)
        - message_count: COUNT(*)
        - duration_minutes: разница между первым и последним сообщением

        Args:
            session: AsyncSession для запросов
            time_range: Tuple (start_time, end_time)

        Returns:
            Список RecentDialog, отсортированный по last_message_at DESC (свежие сверху)
        """
        start_time, end_time = time_range

        # Агрегация по user_id
        stmt = (
            select(
                Message.user_id,
                func.count(Message.id).label("message_count"),
                func.max(Message.created_at).label("last_message_at"),
                # Вычисляем длительность как разницу между max и min created_at
                (
                    func.extract("epoch", func.max(Message.created_at))
                    - func.extract("epoch", func.min(Message.created_at))
                )
                .cast(Integer)
                .label("duration_seconds"),
            )
            .where(
                Message.created_at >= start_time,
                Message.created_at <= end_time,
                Message.deleted_at.is_(None),  # Только не удаленные
            )
            .group_by(Message.user_id)
            .order_by(func.max(Message.created_at).desc())
            .limit(15)
        )

        result = await session.execute(stmt)
        rows = result.all()

        # Преобразуем в список RecentDialog
        recent_dialogs = [
            RecentDialog(
                user_id=row.user_id,
                message_count=row.message_count,
                last_message_at=row.last_message_at,
                duration_minutes=max(1, row.duration_seconds // 60),  # Минимум 1 минута
            )
            for row in rows
        ]

        logger.debug(f"Recent dialogs: {len(recent_dialogs)} entries")

        return recent_dialogs

    async def _get_top_users(
        self, session: AsyncSession, time_range: tuple[datetime, datetime]
    ) -> list[TopUser]:
        """
        Получить топ-10 пользователей по количеству сообщений.

        Бизнес-логика:
        - total_messages: COUNT(messages)
        - dialog_count: количество отдельных дней с активностью
        - last_activity: MAX(created_at)

        Args:
            session: AsyncSession для запросов
            time_range: Tuple (start_time, end_time)

        Returns:
            Список TopUser, отсортированный по total_messages DESC (самые активные сверху)
        """
        start_time, end_time = time_range

        # Агрегация по user_id
        stmt = (
            select(
                Message.user_id,
                func.count(Message.id).label("total_messages"),
                # Для упрощения: dialog_count = количество дней с активностью
                func.count(func.distinct(func.date_trunc("day", Message.created_at))).label(
                    "dialog_count"
                ),
                func.max(Message.created_at).label("last_activity"),
            )
            .where(
                Message.created_at >= start_time,
                Message.created_at <= end_time,
                Message.deleted_at.is_(None),  # Только не удаленные
            )
            .group_by(Message.user_id)
            .order_by(func.count(Message.id).desc())
            .limit(10)
        )

        result = await session.execute(stmt)
        rows = result.all()

        # Преобразуем в список TopUser
        top_users = [
            TopUser(
                user_id=row.user_id,
                total_messages=row.total_messages,
                dialog_count=row.dialog_count,
                last_activity=row.last_activity,
            )
            for row in rows
        ]

        logger.debug(f"Top users: {len(top_users)} entries")

        return top_users
