# Scripts для API

**Дата создания**: 2025-10-17  
**Спринт**: S7 - Real API Integration

---

## 📋 Обзор

Утилиты и скрипты для работы с API: нагрузочное тестирование, профилирование, анализ производительности.

---

## 🔥 Load Testing

### `load_test.py`

Скрипт для нагрузочного тестирования Stats API endpoint.

#### Возможности

- ✅ Параллельные запросы (concurrent users)
- ✅ Настройка количества запросов
- ✅ Метрики производительности (min, max, mean, median, P95, P99)
- ✅ Анализ успешности запросов
- ✅ Throughput (req/s)
- ✅ Performance assessment

#### Запуск

**Базовый запуск** (100 запросов, 10 concurrent):
```bash
cd backend/api
uv run python scripts/load_test.py
```

**С параметрами**:
```bash
# 500 запросов, 50 concurrent users, period=week
uv run python scripts/load_test.py --requests 500 --concurrent 50 --period week

# Тест production сервера
uv run python scripts/load_test.py --url https://api.example.com
```

#### Параметры

| Параметр | Описание | Default | Пример |
|----------|----------|---------|--------|
| `--url` | Base URL API сервера | `http://localhost:8000` | `--url http://api.prod.com` |
| `--period` | Период статистики | `week` | `--period day` |
| `--requests` | Общее количество запросов | `100` | `--requests 1000` |
| `--concurrent` | Параллельных пользователей | `10` | `--concurrent 20` |

#### Пример вывода

```
======================================================================
Starting load test: 100 requests, 10 concurrent
Period: week
Target: http://localhost:8000/api/v1/stats
======================================================================

Warming up API...
Batch 1/10 - 10 concurrent requests
  ✅ 10/10 success, avg time: 45.23ms
Batch 2/10 - 10 concurrent requests
  ✅ 10/10 success, avg time: 2.15ms
...

======================================================================
LOAD TEST RESULTS
======================================================================

Test Date: 2025-10-17T15:30:45
Period: week
Duration: 5.23s

REQUEST SUMMARY:
  Total Requests: 100
  Successful: 100 ✅
  Failed: 0 ❌
  Success Rate: 100.00%
  Throughput: 19.12 req/s

RESPONSE TIMES:
  Min: 1.23ms
  Max: 234.56ms
  Mean: 12.45ms
  Median: 3.21ms
  P95: 45.67ms
  P99: 123.45ms

PERFORMANCE ASSESSMENT:
  🌟 EXCELLENT - P95 < 100ms
  🌟 EXCELLENT - Success rate >= 99%

======================================================================
```

#### Performance Benchmarks

| Режим | P95 | Throughput | Оценка |
|-------|-----|------------|--------|
| **Mock** | < 20ms | 1000+ req/s | 🌟 EXCELLENT |
| **Real (with cache)** | < 50ms | 500+ req/s | 🌟 EXCELLENT |
| **Real (cold)** | < 500ms | 50-100 req/s | ✅ GOOD |

#### Рекомендации по нагрузочному тестированию

**Warmup (прогрев)**:
- Первый запрос всегда медленнее (cold start)
- Скрипт автоматически делает warmup запрос
- Для production тестов сделайте несколько warmup запросов

**Concurrent Users**:
- Начните с малых значений (10-20)
- Постепенно увеличивайте до реальной нагрузки
- Для API с кешем можно 100+ concurrent

**Интерпретация результатов**:
- **P95 < 100ms** - отлично для Real mode
- **P95 < 500ms** - приемлемо
- **P95 > 1s** - требуется оптимизация
- **Success rate < 95%** - проблемы со стабильностью

---

## 🔍 Профилирование SQL запросов

### `analyze_queries.py` (TODO)

Скрипт для анализа производительности SQL запросов с помощью EXPLAIN ANALYZE.

**Планируется**:
- Анализ каждого SQL запроса
- Проверка использования индексов
- Рекомендации по оптимизации

---

## 📊 Пример сценариев тестирования

### Сценарий 1: Проверка после деплоя

```bash
# 1. Запустить API
docker-compose up -d api

# 2. Подождать инициализацию
sleep 5

# 3. Быстрый smoke test
uv run python scripts/load_test.py --requests 50 --concurrent 5

# 4. Проверить что P95 < 100ms и success rate = 100%
```

### Сценарий 2: Тест масштабируемости

```bash
# Постепенно увеличиваем нагрузку

# Level 1: Low
uv run python scripts/load_test.py --requests 100 --concurrent 10

# Level 2: Medium
uv run python scripts/load_test.py --requests 500 --concurrent 50

# Level 3: High
uv run python scripts/load_test.py --requests 1000 --concurrent 100

# Level 4: Extreme
uv run python scripts/load_test.py --requests 2000 --concurrent 200
```

### Сценарий 3: Cache эффективность

```bash
# Тест 1: Cold cache (первые запросы медленные)
docker-compose restart api
sleep 5
uv run python scripts/load_test.py --requests 100 --concurrent 1

# Тест 2: Warm cache (последующие запросы быстрые)
uv run python scripts/load_test.py --requests 100 --concurrent 10

# Сравните P95: должен быть в 10-100 раз быстрее
```

---

## 🐛 Troubleshooting

### Ошибка: "Connection refused"

**Причина**: API не запущен

**Решение**:
```bash
docker-compose up -d api
docker-compose logs -f api
```

### Много failed requests

**Причина**: API перегружен или timeout

**Решение**:
```bash
# Уменьшите concurrent users
uv run python scripts/load_test.py --concurrent 5

# Увеличьте timeout в скрипте (line ~40)
# timeout=30.0 -> timeout=60.0
```

### P95 > 1s

**Причина**: Медленные SQL запросы или нет кеша

**Решение**:
```bash
# Проверьте кеш настройки
echo $CACHE_TTL  # Должно быть 60

# Проверьте индексы БД
docker-compose exec postgres psql -U postgres -d ai_tg_bot -c "\d messages"

# Проверьте connection pool
echo $DB_POOL_SIZE  # Должно быть >= 5
```

---

## 📚 Связанные документы

- [Integration Tests](../tests/integration/README.md) - integration тесты
- [Real Collector](../src/stats/real_collector.py) - тестируемый код
- [Collector Modes](../../../docs/backend/api/collector-modes.md) - переключение Mock/Real

---

**Дата последнего обновления**: 2025-10-17


