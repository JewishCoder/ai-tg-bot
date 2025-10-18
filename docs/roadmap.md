# 🗺️ Roadmap проекта AI Telegram Bot

## 📚 Документация проекта

- **Идея проекта**: [idea.md](idea.md)
- **Техническое видение**: [vision.md](vision.md)

---

## 📊 Легенда статусов

| Статус | Описание |
|--------|----------|
| ⏳ **Планируется** | Спринт запланирован, но не начат |
| 🚧 **В процессе** | Спринт в активной разработке |
| ✅ **Завершено** | Спринт завершен и протестирован |
| 🔄 **На паузе** | Спринт временно приостановлен |
| ❌ **Отменен** | Спринт отменен или не требуется |

---

## 🎯 Таблица спринтов

| Код | Название | Статус | Цель и описание | Состав работ | Фактический план |
|-----|----------|--------|-----------------|--------------|------------------|
| **S0** | **MVP + Качество кода + Отказоустойчивость** | ✅ Завершено | Создание полнофункционального MVP Telegram-бота с интеграцией LLM, внедрение best practices разработки и повышение отказоустойчивости через fallback механизм | • MVP бота (7 итераций)<br>• Технический долг (7 итераций)<br>• Fallback механизм (5 итераций)<br>• Тестирование (85% coverage)<br>• CI/CD Pipeline<br>• Docker Registry | [tasklist-S0.md](tasklists/tasklist-S0.md)<br>[techDebtTasklist-S0.md](tasklists/techDebtTasklist-S0.md)<br>[fallbackTasklist-S0.md](tasklists/fallbackTasklist-S0.md) |
| **S1** | **Хранение данных в Базе данных** | ✅ Завершено | Реализовать сохранение истории диалогов в базе данных вместо файлового хранения. История диалогов должна сохраняться между перезапусками бота | • PostgreSQL + SQLAlchemy 2.0 async<br>• Alembic для миграций<br>• Схема БД (users, messages, user_settings)<br>• Soft delete стратегия<br>• Управляемые лимиты через БД<br>• Рефакторинг Storage<br>• Тесты с моками | [sprint-s1-database.plan.md](../.cursor/plans/sprint-s1-database-4d4dfa9b.plan.md) |
| **S2** | **Технический долг и оптимизации** | ✅ Завершено | Устранение технического долга по результатам code review. Исправление критичных проблем с производительностью и безопасностью, оптимизация работы с БД, улучшение тестирования и документации | • ✅ Блок 1: Критичные исправления (4/4)<br>• ✅ Блок 2: Средние улучшения (5/5)<br>• ✅ Блок 3: Низкоприоритетные (4/4)<br>• 117 тестов (89% coverage)<br>• Security hardening<br>• API документация | [tasklist-S2.md](tasklists/tasklist-S2.md) |
| **S3** | **API Requirements & Mock Implementation** | ✅ Завершено | Разработка требований к дашборду статистики диалогов и реализация Mock API. Проектирование контракта API и архитектуры сборщика статистики | • ✅ Функциональные требования к дашборду<br>• ✅ Контракт API для статистики (KISS)<br>• ✅ Интерфейс StatCollector (Mock/Real)<br>• ✅ Mock реализация StatCollector<br>• ✅ FastAPI приложение и Docker<br>• ✅ Makefile команды и автоматизация<br>• ✅ API документация (архитектура) | [tasklist-S3.md](tasklists/tasklist-S3.md) |
| **S4** | **Frontend Framework Setup** | ✅ Завершено | Создание концепции и инфраструктуры frontend проекта. Выбор технологического стека и настройка инструментов разработки | • ✅ Next.js 15 + TypeScript 5 + npm<br>• ✅ shadcn/ui (10+ компонентов)<br>• ✅ Структура проекта и конфигурация<br>• ✅ ESLint, Prettier, pre-commit hooks<br>• ✅ Vitest + Testing Library<br>• ✅ API client с React Query<br>• ✅ Makefile команды<br>• ✅ Docker конфигурация | [tasklist-S4.md](tasklists/tasklist-S4.md) |
| **S5** | **Dashboard Implementation** | ✅ Завершено | Реализация дашборда статистики диалогов на основе референса и интеграция с Mock API | • ✅ Dashboard Layout с Sidebar и Header<br>• ✅ Period Filter (Day/Week/Month)<br>• ✅ Summary Cards (3 метрики)<br>• ✅ Activity Timeline Chart (Recharts)<br>• ✅ Recent Dialogs & Top Users Tables (Collapsible)<br>• ✅ Responsive Design<br>• ✅ Error/Empty States | [tasklist-S5.md](tasklists/tasklist-S5.md) |
| **S6** | **AI Chat Implementation** | ⏳ Планируется | Реализация веб-чата для администратора с возможностью задавать вопросы по статистике диалогов через text-to-SQL | • API endpoints для чата<br>• Text-to-SQL интеграция<br>• UI компоненты чата<br>• LLM integration для ответов<br>• Real-time updates<br>• Тестирование workflow | Будет создан в Plan Mode |
| **S7** | **Real API Integration** | ✅ Завершено | Переход с Mock API на реальную реализацию с интеграцией с базой данных PostgreSQL | • ✅ Real StatCollector implementation<br>• ✅ Интеграция с БД (PostgreSQL)<br>• ✅ Оптимизация SQL запросов<br>• ✅ Переключение Mock → Real через конфигурацию<br>• ✅ Integration тесты с PostgreSQL<br>• ✅ Документация API обновлена | [tasklist-S7.md](tasklists/tasklist-S7.md) |
| **S8** | **CI/CD Infrastructure для Multi-Service** | ✅ Завершено | Адаптация CI/CD процессов для multi-service архитектуры с полной автоматизацией проверки качества кода и сборки Docker образов для всех сервисов | • ✅ Version Management (4 сервиса)<br>• ✅ API CI/CD Pipeline с PostgreSQL<br>• ✅ Frontend CI/CD Pipeline<br>• ✅ Nginx Dockerfile и CI/CD<br>• ✅ Separate workflows для гибкости<br>• ✅ Docker Compose для production<br>• ✅ Документация CI/CD | [tasklist-S8.md](tasklists/tasklist-S8.md) |
| **S9** | **Production Readiness & Observability** | 🚧 В процессе | Подготовка системы к production deployment на основе результатов code review. Фокус на безопасность, observability, производительность и качество | • ✅ Security Hardening (User Registration, Auth, Rate Limiting, CORS)<br>• ⏳ Observability (Prometheus Metrics, Enhanced Logging)<br>• ⏳ Performance Optimization (DB Queries, Connection Pooling)<br>• ⏳ Testing & Quality (Load Tests, Frontend Unit Tests)<br>• ⏳ DevOps Improvements (Healthchecks, Deployment)<br>• ⏳ Documentation (Диаграммы, Troubleshooting Guide) | [tasklist-S9.md](tasklists/tasklist-S9.md) |

---

## 🌐 Frontend & API Development Phase

### Спринт S3: API Requirements & Mock Implementation

**Цель**: Разработать функциональные требования к дашборду статистики и реализовать Mock API для проверки концепции.

**Состав работ**:

- Формирование функциональных требований к дашборду статистики диалогов
- Проектирование контракта API (REST/GraphQL) - KISS подход, единый endpoint для статистики
- Проектирование интерфейса StatCollector с поддержкой Mock и Real реализаций
- Реализация Mock версии StatCollector с генерацией тестовых данных
- Настройка автоматической генерации API документации (OpenAPI/Swagger)
- Создание entrypoint для запуска API сервера
- Добавление команд в Makefile для запуска API и тестирования endpoints

### Спринт S4: Frontend Framework Setup

**Цель**: Создать архитектурную концепцию frontend проекта, выбрать технологический стек и настроить инфраструктуру разработки.

**Состав работ**:

- Создание документа технического видения frontend (`docs/frontend/front-vision.md`)
- Анализ и выбор оптимального tech stack (React/Vue/Angular, State Management, UI библиотека)
- Создание структуры frontend проекта (директории, конфигурация)
- Настройка инструментов разработки (linter, formatter, bundler)
- Добавление команд для запуска dev-сервера, сборки и проверки качества кода
- Настройка pre-commit hooks и CI/CD для frontend

### Спринт S5: Dashboard Implementation

**Цель**: Реализовать полнофункциональный дашборд статистики диалогов с интеграцией к Mock API.

**Состав работ**:

- **Блок 1**: Dashboard Layout и Period Filter (Day/Week/Month)
- **Блок 2**: Summary Cards компоненты (Total Users, Total Messages, Active Dialogs)
- **Блок 3**: Activity Timeline Chart с Recharts (двойная линия для сообщений и пользователей)
- **Блок 4**: Recent Dialogs и Top Users таблицы с форматированием данных
- **Блок 5**: Responsive Design для всех разрешений, Loading/Error/Empty states
- **Блок 6**: Unit и integration тесты, документация компонентов
- Интеграция date-fns и lucide-react
- Coverage >= 80% для всех dashboard компонентов

### Спринт S6: AI Chat Implementation

**Цель**: Реализовать веб-чат для администратора с возможностью получения аналитики через natural language запросы.

**Состав работ**:

- Разработка API endpoints для чата (WebSocket/REST)
- Интеграция text-to-SQL механизма для преобразования вопросов в SQL запросы
- Реализация UI компонентов чата (message list, input, typing indicators)
- Интеграция с LLM для формирования ответов на основе SQL результатов
- Реализация real-time обновлений (WebSocket/SSE)
- Тестирование полного workflow: вопрос → SQL → результат → ответ LLM

### Спринт S7: Real API Integration

**Цель**: Перейти от Mock реализации к реальному сбору статистики из PostgreSQL базы данных.

**Состав работ**:

- Реализация Real версии StatCollector с подключением к БД
- Написание SQL запросов для агрегации статистики из таблиц messages, users, user_settings
- Оптимизация производительности запросов (индексы, EXPLAIN ANALYZE)
- Реализация переключателя Mock/Real через конфигурацию
- Нагрузочное тестирование и профилирование производительности
- Обновление API документации с реальными схемами данных

### Спринт S8: CI/CD Infrastructure для Multi-Service Architecture

**Цель**: Адаптировать CI/CD процессы для multi-service архитектуры (Bot, API, Frontend, Nginx) с полной автоматизацией проверки качества кода и сборки Docker образов.

**Состав работ**:

- **Блок 1: Version Management**
  - Создать VERSION файлы для всех сервисов: `backend/api/VERSION`, `frontend/VERSION`, `.build/nginx/VERSION`
  - Единая схема версионирования (SemVer)
  - Автоматическое чтение версий в CI workflows

- **Блок 2: API CI/CD Pipeline**
  - Настроить GitHub Actions job для `backend/api`
  - Форматирование (ruff format), линтер (ruff check), проверка типов (mypy)
  - Unit-тесты с coverage >= 70%
  - Интеграционные тесты с PostgreSQL (service container)
  - Docker build и push API образа с версионированием

- **Блок 3: Frontend CI/CD Pipeline**
  - Настроить GitHub Actions job для `frontend`
  - Линтер (ESLint), форматирование (Prettier), проверка типов (TypeScript)
  - Unit-тесты (Vitest) с coverage >= 80%
  - Build проверка (Next.js build)
  - Docker build и push Frontend образа

- **Блок 4: Nginx Configuration & Dockerfile**
  - Создать production-ready `.build/nginx/Dockerfile`
  - Оптимизация образа (alpine base, multi-stage если нужно)
  - Healthcheck endpoint
  - Docker build и push Nginx образа

- **Блок 5: Unified CI/CD Workflow**
  - Объединить все jobs в эффективный workflow
  - Matrix strategy для параллельной сборки сервисов
  - Conditional push (только для main branch)
  - Кэширование зависимостей (pip, npm, docker layers)
  - Настроить зависимости между jobs

- **Блок 6: Docker Compose Production**
  - Обновить `docker-compose.yml` для использования образов из registry
  - Добавить production профили (если нужно)
  - Makefile команды для production деплоя

- **Блок 7: Документация и тесты**
  - Создать документацию CI/CD процессов (`docs/guides/ci-cd.md`)
  - Инструкции по версионированию и релизам
  - Тестирование полного workflow на тестовых ветках

### Спринт S9: Production Readiness & Observability

**Цель**: Подготовить систему к production deployment на основе результатов code review-0002. Устранить найденные проблемы и реализовать рекомендации по безопасности, observability и производительности.

**Состав работ**:

- **Блок 1: Security Hardening** ✅ **ЗАВЕРШЕН** (2025-10-18)
  - ✅ Задача #1.4: User Registration для Stats API на основе admin token (ApiUser модель, миграция)
  - ✅ Задача #1.1: Authentication для Stats API с проверкой через PostgreSQL (Basic Auth)
  - ✅ Задача #1.2: Rate limiting для Stats API (slowapi, 10/minute)
  - ✅ Задача #1.3: CORS middleware для production (whitelist origins, credentials support)
  - ✅ Задача #1.5: Документация по secrets management (Vault/AWS Secrets/K8s)

- **Блок 2: Observability** (High Priority)
  - ✅ Задача #3: Улучшить логирование Real Collector (query timing, slow query warnings)
  - Добавить Prometheus metrics экспорт для Bot:
    - LLM request latency histogram
    - Request rate counter
    - Error rate counter
    - Fallback usage counter
  - Добавить Prometheus metrics экспорт для API:
    - API request latency histogram
    - Database query latency histogram
    - Connection pool metrics
  - Расширить health check endpoints с детальной информацией

- **Блок 3: Performance Optimization** (Medium Priority)
  - Database query optimization:
    - Добавить EXPLAIN ANALYZE для всех сложных запросов Real Collector
    - Query performance logging в development mode
    - Предупреждения о медленных запросах (> 1s)
  - Connection pooling tuning:
    - Увеличить pool_size и max_overflow для production
    - Добавить pool_pre_ping для connection health checks
    - Документировать рекомендованные настройки для разных нагрузок

- **Блок 4: Testing & Quality** (Medium Priority)
  - ✅ Задача #4: Рефакторинг тестовых констант (вынести в константы для переиспользования)
  - ✅ Задача #6: Добавить frontend unit тесты для недостающих компонентов (ActivityChart, PeriodFilter, app-sidebar)
  - Load testing infrastructure:
    - Настроить locust или k6 для нагрузочного тестирования
    - Создать сценарии для Bot и API
    - Документировать результаты baseline performance
  - Contract testing между Frontend и API (опционально)

- **Блок 5: DevOps Improvements** (Low Priority)
  - ✅ Задача #5: Healthcheck improvements в docker-compose (depends_on с condition: service_healthy)
  - Добавить production профили в docker-compose
  - Создать deployment automation scripts
  - Graceful shutdown improvements

- **Блок 6: Documentation** (Low Priority)
  - ✅ Рекомендация #5.1: Создать архитектурные диаграммы (Mermaid):
    - Sequence diagram для LLM request flow (с fallback)
    - Architecture diagram для multi-service системы
    - ER diagram для database schema
  - ✅ Рекомендация #5.2: Создать troubleshooting guide (`docs/guides/troubleshooting.md`):
    - Common errors и их решения
    - Database migration issues
    - LLM API проблемы (rate limits, timeouts, fallback)
    - Docker проблемы
  - Production deployment guide

---

## 📝 Примечания

### О структуре спринтов

Каждый спринт состоит из нескольких итераций, которые детально описаны в соответствующих тасклистах. Тасклисты хранятся в директории `docs/tasklists/` и именуются по шаблону `tasklist-<код спринта>.md`.

### Дата последнего обновления

**Обновлено**: 2025-10-18 (Спринт S9 - Блок 1 завершен)

**История изменений**:

- 2025-10-16: Создан roadmap, добавлен спринт S0
- 2025-10-16: Добавлен спринт S1 (Хранение данных в БД)
- 2025-10-16: Добавлен спринт S2 (Технический долг и оптимизации) на основе code review
- 2025-10-17: Добавлены спринты S3-S7 (Frontend и API развитие): требования к дашборду, Mock API, каркас frontend, реализация dashboard, AI чат, интеграция с Real API
- 2025-10-17: Создан детальный tasklist для Спринта S4 (Frontend Framework Setup) с технологическим стеком: Next.js 15, TypeScript 5, shadcn/ui, Tailwind CSS, npm
- 2025-10-17: Спринт S4 завершен - полностью настроен frontend (Next.js, shadcn/ui, ESLint, Prettier, Vitest, React Query, Docker)
- 2025-10-17: Создан детальный tasklist для Спринта S5 (Dashboard Implementation) - 6 блоков работ для реализации полного дашборда с интеграцией Mock API
- 2025-10-17: Спринт S5 завершен - реализован полнофункциональный dashboard (Sidebar, Period Filter, Summary Cards, Activity Chart, Collapsible Tables, Responsive Design, Error States)
- 2025-10-17: Создан детальный tasklist для Спринта S7 (Real API Integration) - 6 блоков работ для интеграции с PostgreSQL и замены Mock на Real сборщик статистики
- 2025-10-17: Спринт S7 завершен - переход на Real API с PostgreSQL (RealStatCollector, оптимизированные SQL запросы с индексами, конфигурируемое переключение Mock/Real, integration тесты с service container, обновленная документация)
- 2025-10-18: Добавлен спринт S8 (CI/CD Infrastructure для Multi-Service) - адаптация CI/CD для Bot, API, Frontend, Nginx с версионированием и автоматизацией сборки Docker образов
- 2025-10-19: Спринт S8 завершен - полная CI/CD инфраструктура для multi-service архитектуры (4 отдельных workflows, версионирование, автоматическая сборка и публикация Docker образов, production docker-compose, полная документация)
- 2025-10-18: Добавлен спринт S9 (Production Readiness & Observability) на основе code review-0002 - фокус на security hardening (User Registration с admin token, Auth, Rate Limiting), observability (Prometheus metrics), performance optimization, load testing, архитектурные диаграммы и troubleshooting guide
- 2025-10-18: Спринт S9 - Завершен Блок 1 (Security Hardening) - реализованы все 5 задач: User Registration с admin token и ApiUser модель, Basic Auth для Stats API с проверкой через PostgreSQL, Rate Limiting (slowapi, 10/minute), улучшенные CORS настройки, документация по secrets management. CI/CD исправления (Dockerfile context для API, frontend build-args для credentials)

---
