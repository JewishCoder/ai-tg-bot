# 💾 Storage API

## Обзор

`Storage` - класс для работы с историей диалогов и настройками пользователей в PostgreSQL.

## Основные возможности

- ✅ Загрузка и сохранение истории диалогов
- ✅ Soft delete стратегия (сообщения не удаляются физически)
- ✅ Инкрементальное сохранение (UPDATE существующих, INSERT новых)
- ✅ Автоматическое применение лимитов истории
- ✅ Кеширование системных промптов (TTL cache)
- ✅ Error recovery с retry механизмом
- ✅ Транзакционная целостность

## Класс `Storage`

### Инициализация

```python
from src.storage import Storage
from src.database import Database
from src.config import Config

database = Database(config)
storage = Storage(database, config)
```

## Основные методы

### История диалогов

#### `async load_history(user_id: int) -> list[dict[str, str]]`

Загружает полную историю диалога пользователя.

**Параметры:**
- `user_id` (int): Telegram user ID

**Возвращает:**
- `list[dict]`: Список сообщений с полями:
  - `id` (str): UUID сообщения
  - `role` (str): "system" | "user" | "assistant"
  - `content` (str): Текст сообщения
  - `timestamp` (str): ISO 8601 timestamp

**Пример:**
```python
history = await storage.load_history(12345)

for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

#### `async load_recent_history(user_id: int, limit: int | None = None) -> list[dict[str, str]]`

Загружает только последние N сообщений (оптимизированная версия).

**Параметры:**
- `user_id` (int): Telegram user ID
- `limit` (int | None): Максимальное количество сообщений (None = все)

**Возвращает:**
- `list[dict]`: Список последних сообщений в хронологическом порядке

**Пример:**
```python
# Загрузить только последние 20 сообщений
recent = await storage.load_recent_history(12345, limit=20)

# Загрузить все сообщения
all_messages = await storage.load_recent_history(12345, limit=None)
```

**Оптимизация:**
- Использует `ORDER BY created_at DESC LIMIT N`
- Значительно быстрее для пользователей с большой историей
- Результат реверсируется для хронологического порядка

#### `async save_history(user_id: int, messages: list[dict[str, str]]) -> None`

Сохраняет историю диалога с инкрементальным обновлением и retry механизмом.

**Параметры:**
- `user_id` (int): Telegram user ID
- `messages` (list[dict]): Список сообщений для сохранения
  - Поле `id` (optional): UUID существующего сообщения для UPDATE
  - Без `id`: будет создано новое сообщение (INSERT)

**Поведение:**
1. Проверяет существующие UUID в БД
2. UPDATE сообщений с `id`
3. INSERT новых сообщений без `id`
4. Применяет soft delete к старым сообщениям (если превышен лимит)
5. При ошибке делает retry с экспоненциальным backoff

**Retry механизм:**
- Количество попыток: `config.save_retry_attempts` (default: 3)
- Базовая задержка: `config.save_retry_delay` (default: 1.0s)
- Экспоненциальный backoff: `delay * (2 ** (attempt - 1))`

**Пример:**
```python
# Загружаем существующую историю
history = await storage.load_history(user_id)

# Добавляем новые сообщения
history.append({
    "role": "user",
    "content": "Привет!",
    "timestamp": datetime.now(UTC).isoformat()
})

history.append({
    "role": "assistant",
    "content": "Здравствуй!",
    "timestamp": datetime.now(UTC).isoformat()
})

# Сохраняем (инкрементально)
await storage.save_history(user_id, history)
```

#### `async clear_history(user_id: int) -> None`

Очищает историю диалога (soft delete всех сообщений).

**Параметры:**
- `user_id` (int): Telegram user ID

**Пример:**
```python
await storage.clear_history(12345)
```

### Системные промпты

#### `async get_system_prompt(user_id: int) -> str | None`

Получает кастомный системный промпт пользователя (с кешированием).

**Параметры:**
- `user_id` (int): Telegram user ID

**Возвращает:**
- `str | None`: Системный промпт или None (использовать default)

**Кеширование:**
- TTL: `config.cache_ttl` (default: 300s)
- Max size: `config.cache_max_size` (default: 1000)
- Автоматическая инвалидация при `set_system_prompt()`

**Пример:**
```python
prompt = await storage.get_system_prompt(12345)

if prompt:
    print(f"Custom: {prompt}")
else:
    print("Using default prompt")
```

#### `async set_system_prompt(user_id: int, system_prompt: str) -> None`

Устанавливает системный промпт и очищает историю.

**Параметры:**
- `user_id` (int): Telegram user ID
- `system_prompt` (str): Новый системный промпт

**Что происходит:**
1. Очищается история (soft delete)
2. Обновляется `system_prompt` в `user_settings`
3. Создается новое системное сообщение
4. Инвалидируется кеш промптов

**Пример:**
```python
await storage.set_system_prompt(
    12345,
    "Ты - эксперт по Python программированию"
)
```

### Информация о диалоге

#### `async get_dialog_info(user_id: int) -> dict[str, Any]`

Получает статистику о диалоге пользователя.

**Параметры:**
- `user_id` (int): Telegram user ID

**Возвращает:**
- `dict`: Информация о диалоге
  - `messages_count` (int): Количество сообщений
  - `system_prompt` (str | None): Текущий промпт
  - `max_history_messages` (int): Лимит истории
  - `created_at` (str | None): Дата создания
  - `updated_at` (str | None): Дата обновления

**Пример:**
```python
info = await storage.get_dialog_info(12345)

print(f"Сообщений: {info['messages_count']}")
print(f"Лимит: {info['max_history_messages']}")
print(f"Обновлено: {info['updated_at']}")
```

## Приватные методы

### `async _ensure_user_exists(user_id: int) -> None`

Создает пользователя и его настройки, если они не существуют.

- Использует `INSERT ... ON CONFLICT DO NOTHING`
- Thread-safe (idempotent)
- Автоматически вызывается во всех публичных методах

### `async _get_user_settings(user_id: int) -> UserSettings`

Получает настройки пользователя из БД.

### `async _save_history_attempt(user_id: int, messages: list[dict]) -> None`

Внутренний метод для одной попытки сохранения (используется retry механизмом).

## Стратегия Soft Delete

Storage использует soft delete - сообщения не удаляются физически из БД:

```mermaid
graph LR
    A[Активное<br/>сообщение] -->|clear_history| B[deleted_at<br/>IS NOT NULL]
    A -->|Превышен<br/>лимит| B
    
    style A fill:#4CAF50
    style B fill:#F44336
```

**Преимущества:**
- Возможность восстановления данных
- Аудит истории изменений
- Соответствие GDPR (при необходимости)

**Запросы:**
```sql
-- Активные сообщения
SELECT * FROM messages 
WHERE user_id = ? AND deleted_at IS NULL;

-- Soft delete
UPDATE messages 
SET deleted_at = NOW() 
WHERE id IN (?);
```

## Транзакционная целостность

Все операции сохранения выполняются в транзакциях:

```python
async with self.db.session() as session:
    # Все операции внутри одной транзакции
    settings = await session.execute(...)
    existing_ids = await session.execute(...)
    
    # UPDATE/INSERT операции
    await session.execute(...)
    
    # Soft delete старых
    await session.execute(...)
    
    # Автоматический commit при успехе
    # Автоматический rollback при ошибке
```

## Производительность

### Кеширование промптов

```python
# Первый вызов - загрузка из БД
prompt1 = await storage.get_system_prompt(12345)  # DB query

# Последующие вызовы - из кеша
prompt2 = await storage.get_system_prompt(12345)  # Cache HIT
```

### Составной индекс

```sql
CREATE INDEX ix_messages_user_deleted_created 
ON messages (user_id, deleted_at, created_at);
```

Ускоряет запросы типа:
```sql
SELECT * FROM messages 
WHERE user_id = ? AND deleted_at IS NULL 
ORDER BY created_at DESC LIMIT ?;
```

### Инкрементальное сохранение

Вместо `DELETE ALL` + `INSERT ALL`:
```python
# ❌ Плохо: удаляем всё и вставляем заново
DELETE FROM messages WHERE user_id = ?;
INSERT INTO messages VALUES (...);

# ✅ Хорошо: обновляем существующие, добавляем новые
UPDATE messages SET content = ? WHERE id = ?;  -- для существующих
INSERT INTO messages VALUES (...);             -- для новых
```

## Примеры использования

### Полный цикл работы с историей

```python
from src.storage import Storage
from datetime import datetime, UTC

# Инициализация
storage = Storage(database, config)
user_id = 12345

# 1. Загрузка истории
history = await storage.load_recent_history(user_id, limit=20)

if not history:
    # 2. Инициализация для нового пользователя
    prompt = await storage.get_system_prompt(user_id)
    if not prompt:
        prompt = config.system_prompt
        await storage.set_system_prompt(user_id, prompt)
    
    history = [{
        "role": "system",
        "content": prompt,
        "timestamp": datetime.now(UTC).isoformat()
    }]

# 3. Добавление нового сообщения
history.append({
    "role": "user",
    "content": "Привет!",
    "timestamp": datetime.now(UTC).isoformat()
})

# 4. Получение ответа от LLM
response = await llm_client.generate_response(history, user_id)

# 5. Сохранение с ответом
history.append({
    "role": "assistant",
    "content": response,
    "timestamp": datetime.now(UTC).isoformat()
})

await storage.save_history(user_id, history)
```

### Обработка ошибок

```python
try:
    await storage.save_history(user_id, messages)
except Exception as e:
    logger.error(f"Failed to save history: {e}")
    # Retry механизм уже встроен,
    # если мы здесь - все попытки провалились
```

## Атрибуты

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `db` | Database | Объект управления БД |
| `config` | Config | Конфигурация |
| `prompt_cache` | TTLCache | Кеш системных промптов |

## Зависимости

- `src.database.Database`: Управление БД
- `src.config.Config`: Конфигурация
- `src.models`: SQLAlchemy модели
- `cachetools`: TTL кеширование
- `sqlalchemy`: ORM

## См. также

- [Database API](database.md)
- [Models](../../src/models.py)
- [Config](../../src/config.py)

