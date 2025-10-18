# Integration Tests для API

**Дата создания**: 2025-10-17  
**Спринт**: S7 - Real API Integration  
**Обновлено**: 2025-10-17 - Добавлен SQLite in-memory режим

---

## 📋 Обзор

Integration тесты проверяют работу **RealStatCollector** с реальной базой данных.

**Используется PostgreSQL** для integration тестов, так как SQL запросы используют PostgreSQL-специфичные функции (`date_trunc`, `EXTRACT`).

**⚠️ Примечание**: SQLite не поддерживается для integration тестов RealStatCollector из-за несовместимости SQL диалектов.

---

## 🚀 Запуск тестов

### Предварительные требования

**Зависимости установлены**:

```bash
cd backend/api
uv sync --dev
```

### Запуск integration тестов (PostgreSQL)

```bash
cd backend/api

# 1. Запустить PostgreSQL (если еще не запущен)
docker-compose up -d postgres

# 2. Подождать инициализацию БД (5-10 секунд)
timeout /t 10

# 3. Запустить integration тесты
uv run python -m pytest tests/integration/ -v

# С coverage
uv run python -m pytest tests/integration/ --cov=src --cov-report=html

# Конкретный тест
uv run python -m pytest tests/integration/test_real_collector_integration.py::test_real_collector_with_test_data -v

# Исключить integration тесты (запустить только unit)
uv run python -m pytest -m "not integration" -v
```

### Переменные окружения

Можно переопределить параметры подключения к тестовой БД:

```bash
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=ai_tg_bot
export TEST_DB_USER=botuser
export TEST_DB_PASSWORD=botpass

uv run python -m pytest tests/integration/ -v
```

---

## 🧪 Список тестов

### `test_real_collector_integration.py`

| Тест | Описание | Что проверяет |
|------|----------|---------------|
| `test_real_collector_with_empty_database` | Пустая БД | Корректная обработка отсутствия данных |
| `test_real_collector_with_test_data` | Тестовые данные | Корректность всех SQL запросов и статистики |
| `test_real_collector_cache_functionality` | Кеширование | Работа TTL кеша и скорость cached запросов |
| `test_real_collector_soft_delete_handling` | Soft delete | Исключение удалённых сообщений из статистики |
| `test_real_collector_different_periods` | Разные периоды | Корректность фильтрации по времени (day/week/month) |
| `test_real_collector_invalid_period` | Невалидный период | ValueError для неподдерживаемых периодов |
| `test_real_collector_concurrent_requests` | Параллельные запросы | Корректность обработки concurrent запросов |

---

## 🔍 Детали реализации

### Тестовые данные

Все тесты используют `user_id >= 900000` для изоляции:
- `900001-900003` - тесты с test data
- `900010` - тест кеша
- `900020` - тест soft delete
- `900030` - тест разных периодов
- `900040` - тест concurrent requests

### Cleanup

Тестовые данные (user_id >= 900000) автоматически удаляются после каждого теста:

```python
async with engine.begin() as conn:
    await conn.execute(delete(Message).where(Message.user_id >= 900000))
    await conn.execute(delete(UserSettings).where(UserSettings.user_id >= 900000))
    await conn.execute(delete(User).where(User.id >= 900000))
```

---

## ⚠️ Важные замечания

1. **PostgreSQL обязателен**:
   - ⚠️  Не запускайте на production БД!
   - ✅ Используйте dev environment (docker-compose)
   - ✅ Cleanup автоматический (user_id >= 900000)
   - ⚠️  Требует запущенный PostgreSQL

2. **Почему не SQLite?**:
   - ❌ RealStatCollector использует PostgreSQL-специфичные функции (`date_trunc`, `EXTRACT`)
   - ❌ Переписывать SQL для SQLite-совместимости нецелесообразно
   - ✅ Production использует PostgreSQL, тесты должны быть максимально приближены

3. **Windows fix**:
   - ✅ Автоматически переключается на `WindowsSelectorEventLoopPolicy`
   - ℹ️  `psycopg` требует `SelectorEventLoop` вместо дефолтного `ProactorEventLoop`
   - ℹ️  Настроено в `conftest.py`, никаких дополнительных действий не требуется

4. **Performance**:
   - First run (cold): ~5-10s (создание таблиц)
   - Subsequent runs: ~2-3s (только cleanup)
   - Per test: ~200-500ms

---

## 📊 Expected Results

### Успешный запуск (PostgreSQL)

```bash
$ uv run python -m pytest tests/integration/ -v

tests/integration/test_real_collector_integration.py::test_real_collector_with_empty_database PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_with_test_data PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_cache_functionality PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_soft_delete_handling PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_different_periods PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_invalid_period PASSED
tests/integration/test_real_collector_integration.py::test_real_collector_concurrent_requests PASSED

======================== 7 passed in 2.45s =============================
```

### Фильтрация тестов

```bash
# Только integration тесты
$ uv run python -m pytest -m integration -v

# Исключить integration тесты (только unit)
$ uv run python -m pytest -m "not integration" -v

# Все тесты (unit + integration)
$ uv run python -m pytest -v
```

---

## 🐛 Troubleshooting

### Ошибка: "connection refused"

**Причина**: PostgreSQL не запущен

**Решение**:
```bash
# Запустить PostgreSQL
docker-compose up -d postgres

# Подождите 5-10 секунд для инициализации
timeout /t 10

# Проверить что PostgreSQL запущен
docker-compose ps postgres
docker-compose logs postgres
```

### Ошибка: "authentication failed"

**Причина**: Неверные credentials

**Решение**:
```bash
# Проверьте параметры в docker-compose.yml
docker-compose exec postgres psql -U postgres -d ai_tg_bot -c "SELECT 1"

# Или установите правильные переменные окружения
export TEST_DB_USER=postgres
export TEST_DB_PASSWORD=postgres
```

### Ошибка: "no such function: date_trunc"

**Причина**: Тесты запускаются с SQLite вместо PostgreSQL

**Решение**:
```bash
# SQLite НЕ поддерживается для integration тестов
# Используйте PostgreSQL
docker-compose up -d postgres
uv run python -m pytest tests/integration/ -v
```

### Тесты медленные (> 10s)

**Причина**: Медленное подключение или нет индексов

**Решение**:
```bash
# Проверьте индексы в PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_tg_bot -c "\d messages"

# Должны быть индексы:
# - ix_messages_user_deleted_created
# - ix_messages_created_at

# Проверьте latency подключения
docker-compose exec postgres psql -U postgres -d ai_tg_bot -c "SELECT NOW()"
```

---

## 📚 Связанные документы

- [Load Testing](../../scripts/load_test.py) - скрипт нагрузочного тестирования
- [Real Collector](../../src/stats/real_collector.py) - тестируемый код
- [Tasklist S7](../../../../docs/tasklists/tasklist-S7.md) - полный план спринта

---

**Дата последнего обновления**: 2025-10-17

