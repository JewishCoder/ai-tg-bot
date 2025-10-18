# Integration Testing Approach: Бот vs API

**Дата**: 2025-10-17  
**Анализ**: Почему разные подходы для бота и API

---

## 📊 Сравнение подходов

### Backend Bot - SQLite in-memory ✅

**Почему работает**:
```python
# Storage использует базовые SQLAlchemy операции
stmt = select(Message).where(
    Message.user_id == user_id,
    Message.deleted_at.is_(None)  # ✅ Database-agnostic
).order_by(Message.created_at)
```

**Ключевые особенности**:
- ✅ `select()`, `where()`, `order_by()` - работают везде
- ✅ `insert().on_conflict_do_nothing()` - SQLAlchemy транслирует в `INSERT OR IGNORE` для SQLite
- ✅ Никаких PostgreSQL-специфичных функций

**Результат**: SQLite in-memory идеально подходит для тестов

---

### Backend API - PostgreSQL обязателен ⚠️

**Почему НЕ работает SQLite**:
```python
# RealStatCollector использует PostgreSQL-специфичные функции
time_bucket = func.date_trunc("hour", Message.created_at)  # ❌ Только PostgreSQL

duration = func.extract("epoch", func.max(Message.created_at))  # ❌ Только PostgreSQL

days = func.count(
    func.distinct(func.date_trunc("day", Message.created_at))  # ❌ Только PostgreSQL
)
```

**Проблема**: SQLite не поддерживает эти функции:
```
sqlite3.OperationalError: no such function: date_trunc
```

**Ключевые особенности**:
- ❌ `func.date_trunc()` - группировка по часам/дням (только PostgreSQL)
- ❌ `func.extract("epoch", ...)` - извлечение timestamp (только PostgreSQL)
- ❌ Вложенные PostgreSQL-специфичные функции

**Результат**: Требуется PostgreSQL для integration тестов

---

## 🎯 Почему не переписывать SQL?

### Вариант 1: Database-agnostic SQL (отвергнут)

```python
# Для SQLite
if dialect == "sqlite":
    time_bucket = func.strftime("%Y-%m-%d %H:00:00", Message.created_at)
# Для PostgreSQL
else:
    time_bucket = func.date_trunc("hour", Message.created_at)
```

**Проблемы**:
- ❌ Усложняет код
- ❌ Разные результаты в разных БД
- ❌ Тесты не отражают production

### Вариант 2: PostgreSQL для тестов (выбран) ✅

```python
# Один SQL для тестов и production
time_bucket = func.date_trunc("hour", Message.created_at)
```

**Преимущества**:
- ✅ Простой код
- ✅ Тесты = production
- ✅ Предсказуемое поведение

---

## 📋 Итоговое решение

### Backend Bot
- **Тесты**: SQLite in-memory
- **Production**: PostgreSQL
- **Совместимость**: Использует только базовые SQL операции

### Backend API
- **Тесты**: PostgreSQL (через docker-compose)
- **Production**: PostgreSQL
- **Совместимость**: Использует PostgreSQL-специфичные функции

---

## 🔑 Ключевые выводы

1. **SQLite подходит**, если:
   - Используются базовые SQL операции
   - Нет database-specific функций
   - Нужна скорость и изоляция

2. **PostgreSQL обязателен**, если:
   - Используются PostgreSQL-специфичные функции
   - SQL запросы сложные (аналитика, агрегация)
   - Тесты должны полностью соответствовать production

3. **Общий принцип**:
   - Тесты должны использовать ту же БД, что и production
   - Или SQL должен быть полностью database-agnostic
   - Компромиссы усложняют поддержку

4. **Windows специфика**:
   - `psycopg` (async PostgreSQL драйвер) не работает с `ProactorEventLoop`
   - Требуется `WindowsSelectorEventLoopPolicy` для тестов
   - Автоматически настроено в `conftest.py`

---

## 📚 Примеры из кода

### ✅ Database-agnostic (работает в SQLite и PostgreSQL)

```python
# Простой select
stmt = select(Message).where(Message.user_id == user_id)

# Фильтрация
stmt = stmt.where(Message.deleted_at.is_(None))

# Сортировка
stmt = stmt.order_by(Message.created_at.desc())

# Лимит
stmt = stmt.limit(10)

# Агрегация (базовая)
stmt = select(func.count(Message.id))

# Insert with conflict
stmt = insert(User).values(id=user_id).on_conflict_do_nothing()
```

### ❌ PostgreSQL-specific (НЕ работает в SQLite)

```python
# Группировка по часам
func.date_trunc("hour", Message.created_at)

# Извлечение эпохи
func.extract("epoch", timestamp)

# Distinct с вложенными функциями
func.count(func.distinct(func.date_trunc("day", created_at)))

# Array aggregation
func.array_agg(Message.id)

# JSON операции
func.jsonb_agg(...)
```

---

**Дата последнего обновления**: 2025-10-17

