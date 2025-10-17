"""Интеграционные тесты для Storage с реальной БД."""

from datetime import UTC, datetime

import pytest

from src.storage import Storage


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_cycle_save_load_clear(integration_storage: Storage) -> None:
    """
    Тест полного цикла: save -> load -> clear с реальной БД.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 123456
    storage = integration_storage

    # 1. Загружаем пустую историю
    history = await storage.load_history(user_id)
    assert history == []

    # 2. Сохраняем сообщения
    messages_to_save = [
        {
            "role": "system",
            "content": "Ты - полезный ассистент",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        {
            "role": "user",
            "content": "Привет!",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        {
            "role": "assistant",
            "content": "Здравствуй! Чем могу помочь?",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ]
    await storage.save_history(user_id, messages_to_save)

    # 3. Загружаем и проверяем
    loaded_history = await storage.load_history(user_id)
    assert len(loaded_history) == 3
    assert loaded_history[0]["role"] == "system"
    assert loaded_history[1]["role"] == "user"
    assert loaded_history[2]["role"] == "assistant"
    assert loaded_history[1]["content"] == "Привет!"

    # 4. Очищаем историю
    await storage.clear_history(user_id)

    # 5. Проверяем что история пуста
    cleared_history = await storage.load_history(user_id)
    assert cleared_history == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_soft_delete_in_real_db(integration_storage: Storage) -> None:
    """
    Тест soft delete в реальной БД.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 234567
    storage = integration_storage

    # Сохраняем сообщения
    messages = [
        {
            "role": "user",
            "content": f"Message {i}",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        for i in range(5)
    ]
    await storage.save_history(user_id, messages)

    # Проверяем что все сохранились
    history = await storage.load_history(user_id)
    assert len(history) == 5

    # Очищаем (soft delete)
    await storage.clear_history(user_id)

    # Проверяем что load_history не видит удалённые
    history_after_clear = await storage.load_history(user_id)
    assert history_after_clear == []

    # Проверяем что в БД записи остались (soft delete)
    # Для этого загружаем напрямую из БД с учётом deleted_at
    from sqlalchemy import select

    from src.models import Message

    async with storage.db.session() as session:
        stmt = select(Message).where(Message.user_id == user_id)
        result = await session.execute(stmt)
        all_messages = result.scalars().all()

        # Все 5 сообщений должны быть в БД
        assert len(all_messages) == 5
        # Но все должны иметь deleted_at
        assert all(msg.deleted_at is not None for msg in all_messages)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_history_limit_with_real_db(integration_storage: Storage) -> None:
    """
    Тест лимита истории с реальной БД.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 345678
    storage = integration_storage

    # Устанавливаем лимит 10 сообщений через user_settings
    from sqlalchemy import update

    from src.models import UserSettings

    async with storage.db.session() as session:
        # Сначала убедимся что пользователь существует
        await storage._ensure_user_exists(user_id)

    async with storage.db.session() as session:
        stmt = (
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(max_history_messages=10)
        )
        await session.execute(stmt)

    # Сохраняем 15 сообщений
    messages = [
        {
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i}",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        for i in range(15)
    ]
    await storage.save_history(user_id, messages)

    # Проверяем что остались только последние 10
    history = await storage.load_history(user_id)
    assert len(history) == 10

    # Проверяем что это именно последние 10 сообщений
    assert history[0]["content"] == "Message 5"
    assert history[-1]["content"] == "Message 14"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_incremental_save_with_real_db(integration_storage: Storage) -> None:
    """
    Тест инкрементального сохранения с реальной БД.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 456789
    storage = integration_storage

    # 1. Сохраняем начальные сообщения
    initial_messages = [
        {
            "role": "system",
            "content": "System prompt",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        {
            "role": "user",
            "content": "Hello",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ]
    await storage.save_history(user_id, initial_messages)

    # 2. Загружаем с UUID
    loaded = await storage.load_history(user_id)
    assert len(loaded) == 2
    assert "id" in loaded[0]
    assert "id" in loaded[1]

    # 3. Добавляем новое сообщение к существующей истории
    loaded.append(
        {
            "role": "assistant",
            "content": "Hi there!",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
    await storage.save_history(user_id, loaded)

    # 4. Проверяем что теперь 3 сообщения
    final_history = await storage.load_history(user_id)
    assert len(final_history) == 3
    assert final_history[0]["content"] == "System prompt"
    assert final_history[1]["content"] == "Hello"
    assert final_history[2]["content"] == "Hi there!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_custom_prompt_persistence(integration_storage: Storage) -> None:
    """
    Тест сохранения и загрузки кастомного промпта.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 567890
    storage = integration_storage
    custom_prompt = "Ты - эксперт по Python программированию"

    # Устанавливаем кастомный промпт
    await storage.set_system_prompt(user_id, custom_prompt)

    # Загружаем и проверяем
    loaded_prompt = await storage.get_system_prompt(user_id)
    assert loaded_prompt == custom_prompt

    # Проверяем что при загрузке истории есть системное сообщение
    history = await storage.load_history(user_id)
    assert len(history) == 1
    assert history[0]["role"] == "system"
    assert history[0]["content"] == custom_prompt


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_recent_history_limit(integration_storage: Storage) -> None:
    """
    Тест загрузки последних N сообщений с реальной БД.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 678901
    storage = integration_storage

    # Сохраняем 20 сообщений
    messages = [
        {
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i}",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        for i in range(20)
    ]
    await storage.save_history(user_id, messages)

    # Загружаем только последние 5
    recent_history = await storage.load_recent_history(user_id, limit=5)
    assert len(recent_history) == 5

    # Проверяем что это последние 5
    assert recent_history[0]["content"] == "Message 15"
    assert recent_history[-1]["content"] == "Message 19"

    # Загружаем все
    all_history = await storage.load_recent_history(user_id, limit=None)
    assert len(all_history) == 20


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dialog_info_with_real_db(integration_storage: Storage) -> None:
    """
    Тест получения информации о диалоге.

    Args:
        integration_storage: Storage с реальной БД
    """
    user_id = 789012
    storage = integration_storage

    # Сохраняем несколько сообщений
    messages = [
        {"role": "system", "content": "System", "timestamp": datetime.now(UTC).isoformat()},
        {"role": "user", "content": "Hello", "timestamp": datetime.now(UTC).isoformat()},
        {"role": "assistant", "content": "Hi", "timestamp": datetime.now(UTC).isoformat()},
    ]
    await storage.save_history(user_id, messages)

    # Получаем информацию о диалоге
    dialog_info = await storage.get_dialog_info(user_id)

    # Проверяем
    assert dialog_info["messages_count"] == 3
    assert dialog_info["max_history_messages"] == storage.config.max_history_messages
    assert "created_at" in dialog_info
    assert "updated_at" in dialog_info
