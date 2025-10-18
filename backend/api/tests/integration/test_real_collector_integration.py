"""Integration тесты для RealStatCollector с PostgreSQL.

Используется PostgreSQL, так как RealStatCollector использует
PostgreSQL-специфичные SQL функции (date_trunc, EXTRACT).

Требуется запущенный PostgreSQL (docker-compose up -d postgres).
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.database import Database
from src.models import Message, User
from src.stats.real_collector import RealStatCollector


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_with_empty_database(integration_database: Database) -> None:
    """
    Тест RealStatCollector с пустой БД.

    Проверяет что collector корректно обрабатывает отсутствие данных.
    """
    collector = RealStatCollector(integration_database, cache_ttl=1, cache_maxsize=10)

    stats = await collector.get_stats("day")

    # Проверяем что данные пустые но структура корректна
    assert stats.summary.total_users == 0
    assert stats.summary.total_messages == 0
    assert stats.summary.active_dialogs == 0
    assert len(stats.activity_timeline) == 0
    assert len(stats.recent_dialogs) == 0
    assert len(stats.top_users) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_with_test_data(integration_database: Database) -> None:
    """
    Тест RealStatCollector с тестовыми данными.

    Создаёт тестовые данные и проверяет корректность статистики.
    """
    # Создаём тестовые данные
    now = datetime.now(UTC)
    test_user_ids = [900001, 900002, 900003]

    async with integration_database.session() as session:
        # Создаём пользователей
        for user_id in test_user_ids:
            user = User(id=user_id, created_at=now, updated_at=now)
            session.add(user)

        # Создаём сообщения за последние 2 часа
        for i in range(30):
            user_id = test_user_ids[i % len(test_user_ids)]
            created_at = now - timedelta(hours=2) + timedelta(minutes=i * 4)

            message = Message(
                id=uuid4(),
                user_id=user_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Test message {i}",
                content_length=len(f"Test message {i}"),
                created_at=created_at,
                deleted_at=None,
            )
            session.add(message)

        await session.commit()

    # Тестируем collector
    collector = RealStatCollector(integration_database, cache_ttl=1, cache_maxsize=10)

    stats = await collector.get_stats("day")

    # Проверяем Summary
    assert stats.summary.total_users == len(test_user_ids)
    assert stats.summary.total_messages == 30
    assert stats.summary.active_dialogs > 0

    # Проверяем Activity Timeline
    assert len(stats.activity_timeline) > 0
    # Все записи должны быть отсортированы по timestamp
    timestamps = [point.timestamp for point in stats.activity_timeline]
    assert timestamps == sorted(timestamps)

    # Проверяем Recent Dialogs
    assert len(stats.recent_dialogs) > 0
    assert len(stats.recent_dialogs) <= 15  # Лимит
    # Проверка что все user_id из тестовых
    for dialog in stats.recent_dialogs:
        assert dialog.user_id in test_user_ids
        assert dialog.message_count > 0

    # Проверяем Top Users
    assert len(stats.top_users) > 0
    assert len(stats.top_users) <= 10  # Лимит
    # Сортировка по total_messages DESC
    message_counts = [user.total_messages for user in stats.top_users]
    assert message_counts == sorted(message_counts, reverse=True)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_cache_functionality(integration_database: Database) -> None:
    """
    Тест кеширования в RealStatCollector.

    Проверяет что кеш работает корректно и уменьшает время ответа.
    """
    import time

    # Создаём минимальные тестовые данные
    now = datetime.now(UTC)
    async with integration_database.session() as session:
        user = User(id=900010, created_at=now, updated_at=now)
        session.add(user)

        message = Message(
            id=uuid4(),
            user_id=900010,
            role="user",
            content="Test message",
            content_length=12,
            created_at=now,
            deleted_at=None,
        )
        session.add(message)
        await session.commit()

    # Создаём collector с коротким TTL
    collector = RealStatCollector(integration_database, cache_ttl=5, cache_maxsize=10)

    # Первый запрос (без кеша)
    start = time.time()
    stats1 = await collector.get_stats("day")
    first_request_time = time.time() - start

    # Второй запрос (из кеша)
    start = time.time()
    stats2 = await collector.get_stats("day")
    cached_request_time = time.time() - start

    # Проверяем что данные идентичны
    assert stats1.summary.total_users == stats2.summary.total_users
    assert stats1.summary.total_messages == stats2.summary.total_messages

    # Второй запрос должен быть значительно быстрее
    assert cached_request_time < first_request_time
    # Кешированный запрос должен быть < 10ms
    assert cached_request_time < 0.01


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_soft_delete_handling(integration_database: Database) -> None:
    """
    Тест обработки soft delete в RealStatCollector.

    Проверяет что удалённые сообщения не учитываются в статистике.
    """
    now = datetime.now(UTC)

    async with integration_database.session() as session:
        # Создаём пользователя
        user = User(id=900020, created_at=now, updated_at=now)
        session.add(user)

        # Создаём 10 активных сообщений
        for i in range(10):
            message = Message(
                id=uuid4(),
                user_id=900020,
                role="user",
                content=f"Active message {i}",
                content_length=15 + len(str(i)),
                created_at=now - timedelta(hours=1) + timedelta(minutes=i * 5),
                deleted_at=None,  # Активное
            )
            session.add(message)

        # Создаём 5 удалённых сообщений
        for i in range(5):
            message = Message(
                id=uuid4(),
                user_id=900020,
                role="user",
                content=f"Deleted message {i}",
                content_length=16 + len(str(i)),
                created_at=now - timedelta(hours=2) + timedelta(minutes=i * 3),
                deleted_at=now - timedelta(hours=1),  # Удалено
            )
            session.add(message)

        await session.commit()

    collector = RealStatCollector(integration_database, cache_ttl=1, cache_maxsize=10)

    stats = await collector.get_stats("day")

    # Проверяем что учитываются только активные сообщения
    assert stats.summary.total_messages == 10  # Только активные
    assert stats.summary.total_users == 1

    # В recent_dialogs должны быть только активные сообщения
    for dialog in stats.recent_dialogs:
        if dialog.user_id == 900020:
            assert dialog.message_count == 10


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_different_periods(integration_database: Database) -> None:
    """
    Тест работы RealStatCollector с разными периодами (day, week, month).

    Проверяет корректность фильтрации по времени.
    """
    now = datetime.now(UTC)

    async with integration_database.session() as session:
        user = User(id=900030, created_at=now, updated_at=now)
        session.add(user)

        # Сообщения за последний день
        for i in range(5):
            message = Message(
                id=uuid4(),
                user_id=900030,
                role="user",
                content=f"Day message {i}",
                content_length=12 + len(str(i)),
                created_at=now - timedelta(hours=12) + timedelta(hours=i),
                deleted_at=None,
            )
            session.add(message)

        # Сообщения за прошлую неделю (но не сегодня)
        for i in range(3):
            message = Message(
                id=uuid4(),
                user_id=900030,
                role="user",
                content=f"Week message {i}",
                content_length=13 + len(str(i)),
                created_at=now - timedelta(days=3) + timedelta(days=i),
                deleted_at=None,
            )
            session.add(message)

        # Старые сообщения (больше месяца)
        message = Message(
            id=uuid4(),
            user_id=900030,
            role="user",
            content="Old message",
            content_length=11,
            created_at=now - timedelta(days=40),
            deleted_at=None,
        )
        session.add(message)

        await session.commit()

    collector = RealStatCollector(integration_database, cache_ttl=1, cache_maxsize=10)

    # Проверяем period=day (последние 24 часа)
    stats_day = await collector.get_stats("day")
    # Должны быть только сообщения за последний день
    assert stats_day.summary.total_messages >= 5

    # Проверяем period=week (последние 7 дней)
    stats_week = await collector.get_stats("week")
    # Должны быть сообщения за день + за неделю
    assert stats_week.summary.total_messages >= 8

    # Проверяем period=month (последние 30 дней)
    stats_month = await collector.get_stats("month")
    # Должны быть все кроме старого сообщения
    assert stats_month.summary.total_messages >= 8
    # Старое сообщение не должно учитываться
    assert stats_month.summary.total_messages < 9


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_invalid_period(integration_database: Database) -> None:
    """
    Тест обработки невалидного периода.

    Проверяет что collector выбрасывает ValueError для неподдерживаемых периодов.
    """
    collector = RealStatCollector(integration_database, cache_ttl=1, cache_maxsize=10)

    with pytest.raises(ValueError, match="Invalid period"):
        await collector.get_stats("invalid_period")  # type: ignore


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_collector_concurrent_requests(integration_database: Database) -> None:
    """
    Тест параллельных запросов к RealStatCollector.

    Проверяет что collector корректно обрабатывает concurrent запросы.
    """
    import asyncio

    now = datetime.now(UTC)

    # Создаём тестовые данные
    async with integration_database.session() as session:
        user = User(id=900040, created_at=now, updated_at=now)
        session.add(user)

        for i in range(10):
            message = Message(
                id=uuid4(),
                user_id=900040,
                role="user",
                content=f"Concurrent test {i}",
                content_length=15 + len(str(i)),
                created_at=now - timedelta(hours=1) + timedelta(minutes=i * 5),
                deleted_at=None,
            )
            session.add(message)

        await session.commit()

    collector = RealStatCollector(integration_database, cache_ttl=60, cache_maxsize=10)

    # Запускаем 5 параллельных запросов
    tasks = [collector.get_stats("day") for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Все результаты должны быть идентичны
    for result in results[1:]:
        assert result.summary.total_users == results[0].summary.total_users
        assert result.summary.total_messages == results[0].summary.total_messages
