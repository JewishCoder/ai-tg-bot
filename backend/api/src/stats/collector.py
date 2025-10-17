"""Абстрактный интерфейс для сборщиков статистики диалогов."""

from abc import ABC, abstractmethod
from typing import Literal

from .models import StatsResponse

PeriodType = Literal["day", "week", "month"]


class StatCollector(ABC):
    """
    Абстрактный сборщик статистики диалогов.

    Реализует паттерн Strategy для поддержки различных источников данных
    (Mock для разработки, Real для production с подключением к БД).
    """

    @abstractmethod
    async def get_stats(self, period: PeriodType) -> StatsResponse:
        """
        Получить статистику за указанный период.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            StatsResponse с полной статистикой за период:
                - summary: общая статистика
                - activity_timeline: график активности
                - recent_dialogs: последние диалоги
                - top_users: топ пользователи

        Raises:
            ValueError: Если period невалиден
            Exception: При ошибке получения данных
        """
        pass
