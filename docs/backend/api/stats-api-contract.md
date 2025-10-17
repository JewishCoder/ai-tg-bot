# REST API контракт для статистики диалогов

**Версия API**: 1.0  
**Дата создания**: 2025-10-17  
**Статус**: Утверждено

---

## 📋 Обзор

REST API для получения агрегированной статистики диалогов Telegram-бота. Следует принципу KISS - единый endpoint для всех метрик с фильтрацией по периоду.

**Base URL**: `http://localhost:8000/api/v1`

**Формат данных**: JSON  
**Кодировка**: UTF-8  
**Timezone**: UTC (ISO 8601 format)

---

## 🔗 Endpoints

### GET /stats

Получить агрегированную статистику диалогов за указанный период.

#### Query Parameters

| Параметр | Тип | Обязательный | Описание | Значения |
|----------|-----|--------------|----------|----------|
| `period` | string | ✅ Да | Период для статистики | `day`, `week`, `month` |

#### Request Examples

```http
GET /api/v1/stats?period=day HTTP/1.1
Host: localhost:8000
Accept: application/json
```

```http
GET /api/v1/stats?period=week HTTP/1.1
Host: localhost:8000
Accept: application/json
```

```http
GET /api/v1/stats?period=month HTTP/1.1
Host: localhost:8000
Accept: application/json
```

#### Response Schema

**Status**: `200 OK`  
**Content-Type**: `application/json`

```json
{
  "summary": {
    "total_users": 150,
    "total_messages": 4523,
    "active_dialogs": 89
  },
  "activity_timeline": [
    {
      "timestamp": "2025-10-17T00:00:00Z",
      "message_count": 145,
      "active_users": 42
    },
    {
      "timestamp": "2025-10-17T01:00:00Z",
      "message_count": 87,
      "active_users": 28
    }
  ],
  "recent_dialogs": [
    {
      "user_id": 123456789,
      "message_count": 25,
      "last_message_at": "2025-10-17T15:30:00Z",
      "duration_minutes": 45
    },
    {
      "user_id": 987654321,
      "message_count": 18,
      "last_message_at": "2025-10-17T15:15:00Z",
      "duration_minutes": 32
    }
  ],
  "top_users": [
    {
      "user_id": 123456789,
      "total_messages": 523,
      "dialog_count": 45,
      "last_activity": "2025-10-17T15:30:00Z"
    },
    {
      "user_id": 987654321,
      "total_messages": 412,
      "dialog_count": 38,
      "last_activity": "2025-10-17T14:20:00Z"
    }
  ]
}
```

---

## 📊 Response Data Models

### Summary

Общая статистика за период.

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `total_users` | integer | Общее количество пользователей | `150` |
| `total_messages` | integer | Общее количество сообщений (без удаленных) | `4523` |
| `active_dialogs` | integer | Количество активных диалогов (уникальные user_id) | `89` |

**Бизнес-логика**:
- `total_users` - COUNT(DISTINCT users.id) за весь период
- `total_messages` - COUNT(messages) WHERE deleted_at IS NULL
- `active_dialogs` - COUNT(DISTINCT messages.user_id) WHERE deleted_at IS NULL

---

### ActivityPoint

Точка на графике активности.

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `timestamp` | string (ISO 8601) | Метка времени в UTC | `"2025-10-17T10:00:00Z"` |
| `message_count` | integer | Количество сообщений в период | `145` |
| `active_users` | integer | Количество уникальных пользователей | `42` |

**Количество точек**:
- `period=day`: 24 точки (почасовая детализация за последние 24 часа)
- `period=week`: 7 точек (дневная детализация за последние 7 дней)
- `period=month`: 30 точек (дневная детализация за последние 30 дней)

**Сортировка**: По timestamp ASC (от старых к новым)

---

### RecentDialog

Информация о недавнем диалоге.

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `user_id` | integer | Telegram user ID | `123456789` |
| `message_count` | integer | Количество сообщений в диалоге | `25` |
| `last_message_at` | string (ISO 8601) | Время последнего сообщения в UTC | `"2025-10-17T15:30:00Z"` |
| `duration_minutes` | integer | Длительность диалога в минутах | `45` |

**Количество записей**: 10-15 последних диалогов

**Бизнес-логика**:
- Диалог = все сообщения одного пользователя в рамках одной "сессии"
- `duration_minutes` = разница между первым и последним сообщением в сессии

**Сортировка**: По last_message_at DESC (свежие сверху)

---

### TopUser

Топ пользователь по активности.

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `user_id` | integer | Telegram user ID | `123456789` |
| `total_messages` | integer | Общее количество сообщений пользователя | `523` |
| `dialog_count` | integer | Количество отдельных диалогов (сессий) | `45` |
| `last_activity` | string (ISO 8601) | Время последней активности в UTC | `"2025-10-17T15:30:00Z"` |

**Количество записей**: 10 топ пользователей

**Сортировка**: По total_messages DESC (самые активные сверху)

---

### StatsResponse (Root)

Корневой объект ответа.

```typescript
interface StatsResponse {
  summary: Summary;
  activity_timeline: ActivityPoint[];
  recent_dialogs: RecentDialog[];
  top_users: TopUser[];
}
```

**Валидация**:
- Все поля обязательны (required)
- Массивы не могут быть null, только пустые []
- Все timestamp в формате ISO 8601 с timezone UTC
- Все integer >= 0

---

## ⚠️ Error Responses

### 422 Unprocessable Entity

Невалидный параметр `period`.

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["query", "period"],
      "msg": "Input should be 'day', 'week' or 'month'",
      "input": "invalid"
    }
  ]
}
```

**Причины**:
- Параметр `period` отсутствует
- Параметр `period` имеет невалидное значение (не `day`, `week`, `month`)

---

### 500 Internal Server Error

Внутренняя ошибка сервера.

```json
{
  "detail": "Internal server error"
}
```

**Причины**:
- Ошибка при генерации данных в Mock Collector
- Ошибка подключения к БД (в Real Collector)
- Необработанное исключение

---

## 📝 Request/Response Examples

### Example 1: Day Period

**Request**:
```http
GET /api/v1/stats?period=day HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Response** (200 OK):
```json
{
  "summary": {
    "total_users": 123,
    "total_messages": 2847,
    "active_dialogs": 67
  },
  "activity_timeline": [
    {
      "timestamp": "2025-10-16T16:00:00Z",
      "message_count": 98,
      "active_users": 32
    },
    {
      "timestamp": "2025-10-16T17:00:00Z",
      "message_count": 142,
      "active_users": 45
    },
    {
      "timestamp": "2025-10-16T18:00:00Z",
      "message_count": 187,
      "active_users": 56
    }
    // ... еще 21 точка (всего 24)
  ],
  "recent_dialogs": [
    {
      "user_id": 123456789,
      "message_count": 32,
      "last_message_at": "2025-10-17T15:45:00Z",
      "duration_minutes": 67
    },
    {
      "user_id": 234567890,
      "message_count": 18,
      "last_message_at": "2025-10-17T15:30:00Z",
      "duration_minutes": 23
    }
    // ... еще 8-13 записей
  ],
  "top_users": [
    {
      "user_id": 123456789,
      "total_messages": 412,
      "dialog_count": 34,
      "last_activity": "2025-10-17T15:45:00Z"
    },
    {
      "user_id": 345678901,
      "total_messages": 389,
      "dialog_count": 29,
      "last_activity": "2025-10-17T14:20:00Z"
    }
    // ... еще 8 записей (всего 10)
  ]
}
```

---

### Example 2: Week Period

**Request**:
```http
GET /api/v1/stats?period=week HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Response** (200 OK):
```json
{
  "summary": {
    "total_users": 287,
    "total_messages": 8934,
    "active_dialogs": 156
  },
  "activity_timeline": [
    {
      "timestamp": "2025-10-11T00:00:00Z",
      "message_count": 1234,
      "active_users": 89
    },
    {
      "timestamp": "2025-10-12T00:00:00Z",
      "message_count": 1456,
      "active_users": 102
    },
    {
      "timestamp": "2025-10-13T00:00:00Z",
      "message_count": 1123,
      "active_users": 87
    }
    // ... еще 4 точки (всего 7)
  ],
  "recent_dialogs": [
    {
      "user_id": 123456789,
      "message_count": 45,
      "last_message_at": "2025-10-17T15:30:00Z",
      "duration_minutes": 120
    }
    // ... еще 9-14 записей
  ],
  "top_users": [
    {
      "user_id": 123456789,
      "total_messages": 623,
      "dialog_count": 52,
      "last_activity": "2025-10-17T15:30:00Z"
    }
    // ... еще 9 записей
  ]
}
```

---

### Example 3: Month Period

**Request**:
```http
GET /api/v1/stats?period=month HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Response** (200 OK):
```json
{
  "summary": {
    "total_users": 542,
    "total_messages": 34567,
    "active_dialogs": 312
  },
  "activity_timeline": [
    {
      "timestamp": "2025-09-18T00:00:00Z",
      "message_count": 987,
      "active_users": 78
    },
    {
      "timestamp": "2025-09-19T00:00:00Z",
      "message_count": 1123,
      "active_users": 92
    }
    // ... еще 28 точек (всего 30)
  ],
  "recent_dialogs": [
    {
      "user_id": 123456789,
      "message_count": 89,
      "last_message_at": "2025-10-17T15:30:00Z",
      "duration_minutes": 240
    }
    // ... еще 9-14 записей
  ],
  "top_users": [
    {
      "user_id": 123456789,
      "total_messages": 1234,
      "dialog_count": 87,
      "last_activity": "2025-10-17T15:30:00Z"
    }
    // ... еще 9 записей
  ]
}
```

---

### Example 4: Invalid Period (Error)

**Request**:
```http
GET /api/v1/stats?period=year HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["query", "period"],
      "msg": "Input should be 'day', 'week' or 'month'",
      "input": "year",
      "ctx": {
        "expected": "'day', 'week' or 'month'"
      }
    }
  ]
}
```

---

### Example 5: Missing Period (Error)

**Request**:
```http
GET /api/v1/stats HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "period"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## 🔒 Authentication & Authorization

**Версия MVP**: Аутентификация не требуется (развертывание в локальной сети)

**Будущие версии**:
- API Key authentication (Header: `X-API-Key`)
- JWT Bearer tokens
- Rate limiting (100 requests/minute)

---

## 🚀 CORS Configuration

API должен поддерживать CORS для доступа из frontend приложения.

**Allowed Origins** (dev):
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)

**Allowed Methods**:
- `GET`

**Allowed Headers**:
- `Content-Type`
- `Accept`

---

## 📊 Rate Limiting

**Версия MVP**: Без ограничений

**Будущие версии**:
- 100 requests per minute per IP
- Headers:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1634567890

---

## 🧪 Testing

### Health Check Endpoint

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response** (200 OK):
```json
{
  "status": "ok"
}
```

### Manual Testing via curl

```bash
# Day period
curl -X GET "http://localhost:8000/api/v1/stats?period=day"

# Week period
curl -X GET "http://localhost:8000/api/v1/stats?period=week"

# Month period
curl -X GET "http://localhost:8000/api/v1/stats?period=month"

# Invalid period (should return 422)
curl -X GET "http://localhost:8000/api/v1/stats?period=invalid"
```

### Automated Testing

```bash
# Через scripts/test-api.sh
bash scripts/test-api.sh
```

---

## 📈 Performance Requirements

| Метрика | Требование | Примечание |
|---------|------------|------------|
| Response Time | < 200ms | Для Mock API |
| Response Time | < 1000ms | Для Real API (с БД) |
| Availability | 99.9% | Production |
| Max Payload Size | < 1MB | Для любого периода |

---

## 🔄 Versioning

API использует версионирование в URL: `/api/v1/`

**Политика версионирования**:
- Мажорная версия (v1, v2) - breaking changes
- Минорные изменения (добавление полей) - обратно совместимы
- Устаревшие версии поддерживаются 6 месяцев после release новой

---

## 📚 OpenAPI Specification

API автоматически генерирует OpenAPI (Swagger) документацию.

**URLs**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 🔗 Связанные документы

- [Dashboard Requirements](../../frontend/dashboard-requirements.md) - требования к UI
- [Vision](../../vision.md) - техническое видение проекта
- [Roadmap](../../roadmap.md) - план развития

---

## 📝 Changelog

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2025-10-17 | Первая версия контракта для Спринта S3 |

---

**Дата последнего обновления**: 2025-10-17

