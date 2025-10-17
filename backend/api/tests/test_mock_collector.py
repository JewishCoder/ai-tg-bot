"""Тесты для MockStatCollector."""

import pytest

from src.stats.mock_collector import MockStatCollector
from src.stats.models import StatsResponse


class TestMockStatCollector:
    """Тесты для Mock реализации сборщика статистики."""

    @pytest.fixture
    def collector(self) -> MockStatCollector:
        """Фикстура: создает MockStatCollector с фиксированным seed."""
        return MockStatCollector(seed=42)

    @pytest.mark.asyncio
    async def test_get_stats_day(self, collector: MockStatCollector) -> None:
        """Тест: генерация статистики за день."""
        # Act
        result = await collector.get_stats("day")

        # Assert
        assert isinstance(result, StatsResponse)

        # Summary
        assert result.summary.total_users > 0
        assert result.summary.total_messages > 0
        assert result.summary.active_dialogs > 0

        # Activity timeline: 24 точки для дня
        assert len(result.activity_timeline) == 24
        for point in result.activity_timeline:
            assert point.message_count > 0
            assert point.active_users > 0
            assert point.timestamp is not None

        # Recent dialogs: 10-15 записей
        assert 10 <= len(result.recent_dialogs) <= 15
        for dialog in result.recent_dialogs:
            assert dialog.user_id > 0
            assert dialog.message_count >= 1
            assert dialog.duration_minutes >= 0

        # Top users: 10 записей
        assert len(result.top_users) == 10
        for user in result.top_users:
            assert user.user_id > 0
            assert user.total_messages >= 1
            assert user.dialog_count >= 1

    @pytest.mark.asyncio
    async def test_get_stats_week(self, collector: MockStatCollector) -> None:
        """Тест: генерация статистики за неделю."""
        # Act
        result = await collector.get_stats("week")

        # Assert
        assert isinstance(result, StatsResponse)

        # Summary: значения больше чем для дня
        assert result.summary.total_users > 100
        assert result.summary.total_messages > 1000
        assert result.summary.active_dialogs > 50

        # Activity timeline: 7 точек для недели
        assert len(result.activity_timeline) == 7
        for point in result.activity_timeline:
            assert point.message_count > 0
            assert point.active_users > 0

        # Recent dialogs и top users присутствуют
        assert len(result.recent_dialogs) >= 10
        assert len(result.top_users) == 10

    @pytest.mark.asyncio
    async def test_get_stats_month(self, collector: MockStatCollector) -> None:
        """Тест: генерация статистики за месяц."""
        # Act
        result = await collector.get_stats("month")

        # Assert
        assert isinstance(result, StatsResponse)

        # Summary: значения еще больше
        assert result.summary.total_users > 500
        assert result.summary.total_messages > 10000
        assert result.summary.active_dialogs > 500

        # Activity timeline: 30 точек для месяца
        assert len(result.activity_timeline) == 30
        for point in result.activity_timeline:
            assert point.message_count > 0
            assert point.active_users > 0

        # Recent dialogs и top users присутствуют
        assert len(result.recent_dialogs) >= 10
        assert len(result.top_users) == 10

    @pytest.mark.asyncio
    async def test_get_stats_invalid_period(self, collector: MockStatCollector) -> None:
        """Тест: ошибка при невалидном периоде."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid period"):
            await collector.get_stats("year")  # type: ignore

    @pytest.mark.asyncio
    async def test_reproducibility(self) -> None:
        """Тест: воспроизводимость генерации с одинаковым seed."""
        # Arrange
        collector1 = MockStatCollector(seed=100)
        collector2 = MockStatCollector(seed=100)

        # Act
        result1 = await collector1.get_stats("day")
        result2 = await collector2.get_stats("day")

        # Assert: результаты идентичны при одинаковом seed
        assert result1.summary.total_users == result2.summary.total_users
        assert result1.summary.total_messages == result2.summary.total_messages
        assert result1.summary.active_dialogs == result2.summary.active_dialogs
        assert len(result1.activity_timeline) == len(result2.activity_timeline)
        assert len(result1.recent_dialogs) == len(result2.recent_dialogs)
        assert len(result1.top_users) == len(result2.top_users)

    @pytest.mark.asyncio
    async def test_recent_dialogs_sorted(self, collector: MockStatCollector) -> None:
        """Тест: диалоги отсортированы по убыванию времени."""
        # Act
        result = await collector.get_stats("day")

        # Assert: каждый следующий диалог старше предыдущего
        dialogs = result.recent_dialogs
        for i in range(len(dialogs) - 1):
            assert dialogs[i].last_message_at >= dialogs[i + 1].last_message_at

    @pytest.mark.asyncio
    async def test_top_users_sorted(self, collector: MockStatCollector) -> None:
        """Тест: топ пользователи отсортированы по убыванию активности."""
        # Act
        result = await collector.get_stats("day")

        # Assert: каждый следующий пользователь менее активен
        users = result.top_users
        for i in range(len(users) - 1):
            assert users[i].total_messages >= users[i + 1].total_messages

    @pytest.mark.asyncio
    async def test_activity_timeline_order(self, collector: MockStatCollector) -> None:
        """Тест: timeline отсортирован по возрастанию времени."""
        # Act
        result = await collector.get_stats("week")

        # Assert: временные метки идут по возрастанию
        timeline = result.activity_timeline
        for i in range(len(timeline) - 1):
            assert timeline[i].timestamp < timeline[i + 1].timestamp

    @pytest.mark.asyncio
    async def test_pydantic_validation(self, collector: MockStatCollector) -> None:
        """Тест: Pydantic корректно валидирует сгенерированные данные."""
        # Act
        result = await collector.get_stats("day")

        # Assert: модель валидна и может быть сериализована
        json_data = result.model_dump_json()
        assert json_data is not None
        assert len(json_data) > 0

        # Десериализация работает
        deserialized = StatsResponse.model_validate_json(json_data)
        assert deserialized.summary.total_users == result.summary.total_users
