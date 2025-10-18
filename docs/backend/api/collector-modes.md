# Режимы работы StatCollector: Mock vs Real

**Дата создания**: 2025-10-17  
**Версия**: 1.0

---

## 📋 Обзор

API поддерживает два режима работы сборщика статистики:
- **Mock** - генерация тестовых данных (для разработки frontend)
- **Real** - реальные данные из PostgreSQL (production)

Переключение между режимами осуществляется через переменную окружения `COLLECTOR_MODE` без изменения кода.

---

## 🔄 Переключение режимов

### Через переменную окружения

```bash
# Mock режим (default)
export COLLECTOR_MODE=mock

# Real режим
export COLLECTOR_MODE=real
```

### Через .env файл

```bash
# backend/api/.env
COLLECTOR_MODE=real

# PostgreSQL настройки (обязательны для real режима)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_tg_bot
DB_USER=postgres
DB_PASSWORD=your_password
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Cache settings
CACHE_TTL=60          # Cache TTL in seconds
CACHE_MAXSIZE=100     # Cache max size
```

---

## 🚀 Запуск в разных режимах

### Mock режим (разработка)

Используется для разработки frontend без подключения к базе данных.

```bash
cd backend/api

# Через переменную окружения
COLLECTOR_MODE=mock uvicorn src.app:app --reload

# Или через .env файл
echo "COLLECTOR_MODE=mock" > .env
uvicorn src.app:app --reload
```

**Логи при запуске**:
```
INFO - Starting AI TG Bot Stats API
INFO - API Version: 1.0.0
INFO - Collector Mode: mock
INFO - Creating MockStatCollector (test data generator)
```

### Real режим (production)

Требует доступ к PostgreSQL базе данных бота.

```bash
cd backend/api

# Через переменную окружения
COLLECTOR_MODE=real \
DB_HOST=localhost \
DB_PORT=5432 \
DB_NAME=ai_tg_bot \
DB_USER=postgres \
DB_PASSWORD=your_password \
uvicorn src.app:app --host 0.0.0.0 --port 8000

# Или через .env файл
cat > .env << EOF
COLLECTOR_MODE=real
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_tg_bot
DB_USER=postgres
DB_PASSWORD=your_password
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
CACHE_TTL=60
CACHE_MAXSIZE=100
EOF

uvicorn src.app:app --host 0.0.0.0 --port 8000
```

**Логи при запуске**:
```
INFO - Starting AI TG Bot Stats API
INFO - API Version: 1.0.0
INFO - Collector Mode: real
INFO - Creating RealStatCollector (PostgreSQL backend)
INFO - Database initialized: pool_size=5, max_overflow=10
INFO - RealStatCollector initialized with PostgreSQL backend
```

---

## ✅ Проверка текущего режима

### 1. Через логи приложения

При старте API в логах отображается текущий режим:

```
INFO - Collector Mode: mock
# или
INFO - Collector Mode: real
```

### 2. Через health check endpoint

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. Проверка данных

**Mock режим** возвращает одинаковые данные (seed=42):
```bash
curl "http://localhost:8000/api/v1/stats?period=day"
# Данные всегда одинаковые при одинаковом seed
```

**Real режим** возвращает актуальные данные из БД:
```bash
curl "http://localhost:8000/api/v1/stats?period=day"
# Данные меняются в зависимости от содержимого БД
```

---

## ⚙️ Настройки для Real режима

### Обязательные параметры

| Параметр | Описание | Default | Пример |
|----------|----------|---------|--------|
| `COLLECTOR_MODE` | Режим работы | `mock` | `real` |
| `DB_HOST` | PostgreSQL host | `localhost` | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` | `5432` |
| `DB_NAME` | Имя базы данных | `ai_tg_bot` | `ai_tg_bot` |
| `DB_USER` | Пользователь БД | `postgres` | `postgres` |
| `DB_PASSWORD` | Пароль БД | `postgres` | `your_password` |

### Опциональные параметры (производительность)

| Параметр | Описание | Default | Рекомендация |
|----------|----------|---------|--------------|
| `DB_POOL_SIZE` | Размер пула соединений | `5` | `5-10` |
| `DB_MAX_OVERFLOW` | Макс. доп. соединений | `10` | `10-20` |
| `CACHE_TTL` | Время жизни кеша (секунды) | `60` | `30-300` |
| `CACHE_MAXSIZE` | Макс. размер кеша | `100` | `100-1000` |

### Connection String формат

Real режим использует `psycopg3` драйвер:

```
postgresql+psycopg://user:password@host:port/dbname
```

**Пример**:
```
postgresql+psycopg://postgres:mypassword@localhost:5432/ai_tg_bot
```

---

## 📊 Сравнение режимов

### Mock Mode

**Преимущества**:
- ✅ Не требует базу данных
- ✅ Мгновенная генерация данных (~10ms)
- ✅ Идеально для разработки frontend
- ✅ Детерминированные данные (seed=42)
- ✅ Высокая пропускная способность (1000+ RPS)

**Недостатки**:
- ❌ Данные не реальные
- ❌ Нет связи с реальной статистикой бота

**Use Case**: Frontend development, демонстрации, тестирование UI

### Real Mode

**Преимущества**:
- ✅ Реальные данные из PostgreSQL
- ✅ Актуальная статистика бота
- ✅ Production ready
- ✅ Кеширование для производительности

**Недостатки**:
- ❌ Требует подключение к БД
- ❌ Медленнее Mock режима (~100-500ms без кеша)
- ❌ Требует настройку connection pooling

**Use Case**: Production deployment, реальная аналитика

---

## 📈 Performance Metrics

### Mock Mode

| Метрика | Значение |
|---------|----------|
| Response Time (avg) | ~10ms |
| Response Time (p95) | ~15ms |
| Throughput | 1000+ RPS |
| CPU Usage | Низкое |
| Memory Usage | Минимальное |

### Real Mode (без кеша)

| Метрика | Значение |
|---------|----------|
| Response Time (avg) | ~200ms |
| Response Time (p95) | ~500ms |
| Throughput | 50-100 RPS |
| CPU Usage | Среднее |
| Memory Usage | Среднее (connection pool) |

### Real Mode (с кешем, TTL=60s)

| Метрика | Значение |
|---------|----------|
| Response Time (avg) | ~1ms |
| Response Time (p95) | ~5ms |
| Throughput | 1000+ RPS |
| Cache Hit Rate | ~80% (после прогрева) |

---

## 🔧 Troubleshooting

### Ошибка: "Invalid COLLECTOR_MODE: ..."

**Причина**: Неверное значение переменной `COLLECTOR_MODE`

**Решение**:
```bash
# Проверить текущее значение
echo $COLLECTOR_MODE

# Установить правильное значение
export COLLECTOR_MODE=mock  # или real
```

### Ошибка: "Database connection failed"

**Причина**: Не удается подключиться к PostgreSQL в Real режиме

**Решение**:
1. Проверить что PostgreSQL запущен:
   ```bash
   docker ps | grep postgres
   ```

2. Проверить параметры подключения:
   ```bash
   psql -h localhost -p 5432 -U postgres -d ai_tg_bot
   ```

3. Проверить логи API:
   ```bash
   # Ищем ошибки подключения
   tail -f logs/api.log | grep "Database"
   ```

### Mock режим возвращает одинаковые данные

**Причина**: Mock использует фиксированный seed=42 для воспроизводимости

**Решение**: Это нормальное поведение. Для разных данных используйте Real режим.

### Real режим медленный

**Причина**: Не используется кеш или плохая настройка БД

**Решение**:
1. Включить кеш (по умолчанию включен):
   ```bash
   CACHE_TTL=60  # 60 секунд
   ```

2. Увеличить connection pool:
   ```bash
   DB_POOL_SIZE=10
   DB_MAX_OVERFLOW=20
   ```

3. Проверить индексы БД:
   ```sql
   -- Должен быть composite index на messages
   \d messages
   -- ix_messages_user_deleted_created (user_id, deleted_at, created_at)
   ```

---

## 🧪 Тестирование переключения режимов

### 1. Запустить в Mock режиме

```bash
cd backend/api
COLLECTOR_MODE=mock uvicorn src.app:app --reload
```

### 2. Проверить endpoint

```bash
curl "http://localhost:8000/api/v1/stats?period=day" | jq .summary
```

**Ожидаемый результат (Mock)**:
```json
{
  "total_users": 123,
  "total_messages": 2847,
  "active_dialogs": 67
}
```

### 3. Переключить на Real режим

```bash
# Остановить API (Ctrl+C)

# Установить Real режим
export COLLECTOR_MODE=real
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ai_tg_bot
export DB_USER=postgres
export DB_PASSWORD=postgres

# Запустить снова
uvicorn src.app:app --reload
```

### 4. Проверить endpoint снова

```bash
curl "http://localhost:8000/api/v1/stats?period=day" | jq .summary
```

**Ожидаемый результат (Real)**:
```json
{
  "total_users": 5,
  "total_messages": 142,
  "active_dialogs": 3
}
```

Данные будут отличаться от Mock режима и соответствовать реальной БД.

---

## 📚 Связанные документы

- [Real API Architecture](real-api-architecture.md) - архитектура Real API
- [Stats API Contract](stats-api-contract.md) - контракт API
- [Mock Collector](mock-collector.md) - Mock реализация

---

## 📝 Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2025-10-17 | Первая версия документации для Спринта S7 |

---

**Дата последнего обновления**: 2025-10-17


