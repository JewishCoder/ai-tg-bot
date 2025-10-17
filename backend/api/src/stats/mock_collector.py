"""Mock реализация сборщика статистики с генерацией тестовых данных."""

import logging
import random
from datetime import UTC, datetime, timedelta

from .collector import PeriodType, StatCollector
from .models import ActivityPoint, RecentDialog, StatsResponse, Summary, TopUser

logger = logging.getLogger(__name__)


class MockStatCollector(StatCollector):
    """
    Mock реализация сборщика статистики.

    Генерирует реалистичные тестовые данные с естественными вариациями
    для разработки frontend без подключения к реальной базе данных.

    Attributes:
        _random: Random generator с фиксированным seed для воспроизводимости
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Инициализация Mock collector.

        Args:
            seed: Seed для генератора случайных чисел (по умолчанию 42)
        """
        self._random = random.Random(seed)
        logger.info(f"MockStatCollector initialized with seed={seed}")

    async def get_stats(self, period: PeriodType) -> StatsResponse:
        """
        Генерирует Mock данные для указанного периода.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с сгенерированными данными

        Raises:
            ValueError: Если period невалиден
        """
        if period not in ("day", "week", "month"):
            raise ValueError(f"Invalid period: {period}. Must be 'day', 'week' or 'month'")

        logger.info(f"Generating mock stats for period={period}")

        # Генерация данных в зависимости от периода
        summary = self._generate_summary(period)
        activity_timeline = self._generate_activity_timeline(period)
        recent_dialogs = self._generate_recent_dialogs()
        top_users = self._generate_top_users()

        return StatsResponse(
            summary=summary,
            activity_timeline=activity_timeline,
            recent_dialogs=recent_dialogs,
            top_users=top_users,
        )

    def _generate_summary(self, period: PeriodType) -> Summary:
        """
        Генерирует общую статистику.

        Значения зависят от периода: чем длиннее период, тем больше значения.
        """
        period_multipliers = {"day": 1.0, "week": 3.5, "month": 15.0}
        multiplier = period_multipliers[period]

        return Summary(
            total_users=int(self._random.randint(100, 200) * multiplier),
            total_messages=int(self._random.randint(1000, 3000) * multiplier),
            active_dialogs=int(self._random.randint(50, 150) * multiplier),
        )

    def _generate_activity_timeline(self, period: PeriodType) -> list[ActivityPoint]:
        """
        Генерирует timeline активности.

        - day: 24 точки (почасовые за последние 24 часа)
        - week: 7 точек (дневные за последние 7 дней)
        - month: 30 точек (дневные за последние 30 дней)

        Применяет естественные вариации (пики днем, спады ночью).
        """
        now = datetime.now(UTC)

        if period == "day":
            points_count = 24
            time_delta = timedelta(hours=1)
            base_message_count = 100
        elif period == "week":
            points_count = 7
            time_delta = timedelta(days=1)
            base_message_count = 1000
        else:  # month
            points_count = 30
            time_delta = timedelta(days=1)
            base_message_count = 800

        points: list[ActivityPoint] = []
        for i in range(points_count):
            timestamp = now - time_delta * (points_count - i - 1)

            # Естественные вариации: больше активности в определенные часы/дни
            if period == "day":
                # Пики в дневное время (10:00-22:00)
                hour = timestamp.hour
                activity_factor = 1.5 if 10 <= hour <= 22 else 0.5
            else:
                # Будние дни активнее выходных
                weekday = timestamp.weekday()
                activity_factor = 1.2 if weekday < 5 else 0.7

            message_count = int(
                base_message_count * activity_factor * self._random.uniform(0.8, 1.2)
            )
            active_users = int(message_count * self._random.uniform(0.2, 0.4))

            points.append(
                ActivityPoint(
                    timestamp=timestamp,
                    message_count=max(1, message_count),
                    active_users=max(1, active_users),
                )
            )

        return points

    def _generate_recent_dialogs(self) -> list[RecentDialog]:
        """
        Генерирует список недавних диалогов.

        Возвращает 10-15 диалогов с убыванием временных меток.
        """
        dialogs_count = self._random.randint(10, 15)
        now = datetime.now(UTC)
        dialogs: list[RecentDialog] = []

        for i in range(dialogs_count):
            # Диалоги за последние несколько часов
            hours_ago = i * self._random.uniform(0.5, 2.0)
            last_message_at = now - timedelta(hours=hours_ago)

            dialogs.append(
                RecentDialog(
                    user_id=self._random.randint(100000000, 999999999),
                    message_count=self._random.randint(5, 50),
                    last_message_at=last_message_at,
                    duration_minutes=self._random.randint(10, 180),
                )
            )

        # Сортировка по убыванию времени (свежие сверху)
        return sorted(dialogs, key=lambda d: d.last_message_at, reverse=True)

    def _generate_top_users(self) -> list[TopUser]:
        """
        Генерирует топ пользователей по активности.

        Возвращает 10 пользователей, отсортированных по количеству сообщений.
        """
        users_count = 10
        now = datetime.now(UTC)
        users: list[TopUser] = []

        # Генерируем с убыванием активности
        base_messages = 1000
        for _ in range(users_count):
            total_messages = int(base_messages * self._random.uniform(0.7, 0.95))
            base_messages = total_messages  # Следующий пользователь менее активен

            users.append(
                TopUser(
                    user_id=self._random.randint(100000000, 999999999),
                    total_messages=total_messages,
                    dialog_count=self._random.randint(10, 100),
                    last_activity=now - timedelta(hours=self._random.uniform(0, 48)),
                )
            )

        return users
