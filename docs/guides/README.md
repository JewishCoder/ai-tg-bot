# 📚 Руководства по проекту AI Telegram Bot

> **Цель:** Полное руководство для онбординга разработчиков, DevOps и контрибьюторов

## 🗺️ Карта обучения

### Для новичков (Quick Start)
1. [🎨 Visual Guide](#visual-guide) - **НАЧНИ ОТСЮДА!** Визуальный обзор архитектуры
2. [Getting Started](#getting-started) - Первый запуск за 30 минут *(скоро)*
3. [Repository Tour](#repository-tour) - Экскурсия по структуре проекта *(скоро)*

### Для разработчиков
4. [Architecture](#architecture) - Архитектурные решения и паттерны *(скоро)*
5. [Data Model](#data-model) - Модели данных и их lifecycle *(скоро)*
6. [Development Workflow](#development-workflow) - TDD цикл разработки *(скоро)*
7. [Testing](#testing) - Comprehensive testing guide *(скоро)*

### Для DevOps / интеграторов
8. [Configuration](#configuration) - Полное руководство по конфигурации *(скоро)*
9. [Integrations](#integrations) - Внешние API и интеграции *(скоро)*
10. [Deployment](#deployment) - От Docker до production *(скоро)*
11. [CI/CD](#cicd) - GitHub Actions workflow *(скоро)*

### Для контрибьюторов
12. [Code Review](#code-review) - Процесс ревью и стандарты *(скоро)*
13. [Troubleshooting](#troubleshooting) - Решение типичных проблем *(скоро)*
14. [Security](#security) - Security best practices *(скоро)*

---

## 📖 Доступные гайды

### 🎨 Visual Guide
**Статус:** ✅ Готов  
**Файл:** [`VISUAL_GUIDE.md`](./VISUAL_GUIDE.md)  
**Время чтения:** 20-30 минут  
**Аудитория:** Все

**Содержание:**
Comprehensive визуализация проекта с использованием Mermaid диаграмм:
- 🏗️ High-Level Architecture (System Context, Application Layers)
- 📦 Component Structure (Module Dependencies, Directory Tree)
- 🔄 Data Flow (Message Processing, Data Lifecycle)
- 📊 Sequence Diagrams (Message Flow, Fallback, Role Change)
- 🔄 State Machines (Message Handler, Storage, LLM Retry)
- 🚀 Deployment Architecture (Development, Production, Docker Build)
- 🔧 CI/CD Pipeline (GitHub Actions, Release Process)
- ⚠️ Error Handling Flow (Error Hierarchy, Retry Strategy)
- 💾 Storage Architecture (JSON Structure, Operations)
- 🏛️ Class Diagram (Core Classes, Handlers)
- 🛠️ Technology Stack

**Почему начинать с этого гайда?**
- Визуальное представление всей системы за 20 минут
- Понимание архитектуры без чтения кода
- Ссылки на детальные гайды для углубления

---

### 🚀 Getting Started
**Статус:** 🚧 Планируется  
**Файл:** `GETTING_STARTED.md`  
**Время:** 30-60 минут  
**Аудитория:** Новички

**Планируемое содержание:**
- Prerequisites (Python, uv, Docker)
- Получение токенов (BotFather, OpenRouter)
- Установка и настройка (Windows/Linux/Mac)
- Первый запуск локально
- Первое взаимодействие в Telegram
- Troubleshooting типичных проблем
- Что дальше? (ссылки на следующие шаги)

---

### 🗺️ Repository Tour
**Статус:** 🚧 Планируется  
**Файл:** `REPOSITORY_TOUR.md`  
**Время:** 20 минут  
**Аудитория:** Новички, разработчики

**Планируемое содержание:**
- Интерактивный тур по структуре проекта
- Описание каждой директории
- Ключевые файлы и их назначение
- Naming conventions
- "Карта" зависимостей между модулями
- FAQ: "Где находится X?"

---

### 🏗️ Architecture
**Статус:** 🚧 Планируется  
**Файл:** `ARCHITECTURE.md`  
**Время:** 1-2 часа  
**Аудитория:** Разработчики, архитекторы

**Планируемое содержание:**
- Архитектурные паттерны (SOLID, DI, Async)
- Обоснование технических решений
- Trade-offs и альтернативы
- Async architecture deep dive
- Fallback механизм (детали)
- Architecture Decision Records (ADR)
- Расширяемость и масштабирование

---

### 📊 Data Model
**Статус:** 🚧 Планируется  
**Файл:** `DATA_MODEL.md`  
**Время:** 30-45 минут  
**Аудитория:** Разработчики

**Планируемое содержание:**
- Модель сообщения (Message format)
- История диалога (Dialog structure)
- JSON schema для storage файлов
- Pydantic модели (Config)
- Lifecycle данных
- Примеры реальных данных
- Миграции данных

---

### ⚙️ Configuration
**Статус:** 🚧 Планируется  
**Файл:** `CONFIGURATION.md`  
**Время:** 30 минут  
**Аудитория:** Все, особенно DevOps

**Планируемое содержание:**
- Все параметры `.env` с подробным описанием
- Обязательные vs опциональные
- Environment-specific конфигурация
- Секреты (как хранить, ротировать)
- Примеры для разных сценариев
- Troubleshooting конфигурации

---

### 🌐 Integrations
**Статус:** 🚧 Планируется  
**Файл:** `INTEGRATIONS.md`  
**Время:** 45 минут  
**Аудитория:** DevOps, разработчики

**Планируемое содержание:**
- **Telegram Bot API** (polling, rate limits)
- **OpenRouter API** (модели, токены, pricing)
- **Fallback механизм** (детали)
- Альтернативы OpenRouter
- Мониторинг внешних API
- Обработка downtime

---

### 🚀 Deployment
**Статус:** 🚧 Планируется  
**Файл:** `DEPLOYMENT.md`  
**Время:** 1 час  
**Аудитория:** DevOps

**Планируемое содержание:**
- Локальный deployment (Docker Compose, Systemd)
- Cloud deployment (Yandex Cloud, AWS, GCP)
- Kubernetes (для scaling)
- Environment setup
- Monitoring setup
- Backup и recovery
- Scaling considerations

---

### 🔧 CI/CD
**Статус:** 🚧 Планируется  
**Файл:** `CI_CD.md`  
**Время:** 30-45 минут  
**Аудитория:** DevOps, разработчики

**Планируемое содержание:**
- GitHub Actions workflow (детальный разбор)
- Версионирование (VERSION file)
- Branching strategy
- Pull Request checklist
- Release process
- CI troubleshooting

---

### 🔄 Development Workflow
**Статус:** 🚧 Планируется  
**Файл:** `DEVELOPMENT_WORKFLOW.md`  
**Время:** 1-2 часа  
**Аудитория:** Контрибьюторы

**Планируемое содержание:**
- Подготовка окружения (детально)
- TDD workflow (Red → Green → Refactor)
- Feature development (от задачи до PR)
- Local testing
- Debugging async кода
- Common pitfalls

---

### 🧪 Testing
**Статус:** 🚧 Планируется  
**Файл:** `TESTING.md`  
**Время:** 1 час  
**Аудитория:** Разработчики

**Планируемое содержание:**
- Testing philosophy
- Test types (unit, integration, e2e)
- Pytest guide (fixtures, async, mocking)
- Coverage (как измерять, цели)
- Test data management
- CI testing
- Performance testing

---

### 👀 Code Review
**Статус:** 🚧 Планируется  
**Файл:** `CODE_REVIEW.md`  
**Время:** 30 минут  
**Аудитория:** Контрибьюторы

**Планируемое содержание:**
- Pull Request guidelines
- Code review process
- Quality gates
- Approval workflow
- Common review comments
- Anti-patterns

---

### 🔧 Troubleshooting
**Статус:** 🚧 Планируется  
**Файл:** `TROUBLESHOOTING.md`  
**Время:** По необходимости  
**Аудитория:** Все

**Планируемое содержание:**
- Диагностика по симптомам
- Где смотреть логи
- Как интерпретировать ошибки
- FAQ
- Контакты для escalation

---

### 🔒 Security
**Статус:** 🚧 Планируется  
**Файл:** `SECURITY.md`  
**Время:** 45 минут  
**Аудитория:** DevOps, разработчики

**Планируемое содержание:**
- Секреты и токены (хранение, ротация)
- API security (rate limiting, validation)
- Docker security
- Dependencies (vulnerability scanning)
- Data privacy (GDPR)
- Incident response

---

## 🎯 Рекомендуемые треки обучения

### 🌱 Track 1: Новичок → Первый запуск
**Цель:** Запустить бота и понять базовую структуру

1. [🎨 Visual Guide](./VISUAL_GUIDE.md) ✅ - Визуальный обзор (30 мин)
2. 🚀 Getting Started *(скоро)* - Первый запуск (30 мин)
3. 🗺️ Repository Tour *(скоро)* - Структура проекта (20 мин)

**Итого:** ~1.5 часа  
**Результат:** Работающий бот + понимание структуры

---

### 💻 Track 2: Разработчик → Первый PR
**Цель:** Внести первый вклад в проект

1. [🎨 Visual Guide](./VISUAL_GUIDE.md) ✅ - Архитектура (30 мин)
2. 🚀 Getting Started *(скоро)* - Setup окружения (30 мин)
3. 🏗️ Architecture *(скоро)* - Глубокое понимание (1 час)
4. 🔄 Development Workflow *(скоро)* - TDD процесс (1 час)
5. 🧪 Testing *(скоро)* - Написание тестов (1 час)
6. 👀 Code Review *(скоро)* - Создание PR (30 мин)

**Итого:** ~5 часов  
**Результат:** Первый merged PR

---

### 🚀 Track 3: DevOps → Production Deploy
**Цель:** Развернуть бота в production

1. [🎨 Visual Guide](./VISUAL_GUIDE.md) ✅ - Deployment архитектура (15 мин)
2. ⚙️ Configuration *(скоро)* - Настройка окружения (30 мин)
3. 🌐 Integrations *(скоро)* - Внешние API (30 мин)
4. 🚀 Deployment *(скоро)* - Production setup (1 час)
5. 🔧 CI/CD *(скоро)* - Pipeline (30 мин)
6. 🔧 Troubleshooting *(скоро)* - Операционная поддержка (30 мин)

**Итого:** ~3.5 часа  
**Результат:** Production deployment

---

### 🏛️ Track 4: Архитектор → Полное понимание
**Цель:** Глубокое понимание всех аспектов

1. [🎨 Visual Guide](./VISUAL_GUIDE.md) ✅ - Обзор системы (30 мин)
2. 🏗️ Architecture *(скоро)* - Архитектурные решения (2 часа)
3. 📊 Data Model *(скоро)* - Модели данных (45 мин)
4. 🌐 Integrations *(скоро)* - Внешние зависимости (45 мин)
5. 🔒 Security *(скоро)* - Security considerations (45 мин)
6. 🔧 Troubleshooting *(скоро)* - Edge cases (30 мин)

**Итого:** ~5 часов  
**Результат:** Экспертное понимание проекта

---

## 📂 Структура директории

```
docs/guides/
├── README.md                    # 📖 Этот файл (индекс)
├── VISUAL_GUIDE.md             # ✅ Визуальная архитектура
├── GETTING_STARTED.md          # 🚧 Планируется
├── REPOSITORY_TOUR.md          # 🚧 Планируется
├── ARCHITECTURE.md             # 🚧 Планируется
├── DATA_MODEL.md               # 🚧 Планируется
├── CONFIGURATION.md            # 🚧 Планируется
├── INTEGRATIONS.md             # 🚧 Планируется
├── DEPLOYMENT.md               # 🚧 Планируется
├── CI_CD.md                    # 🚧 Планируется
├── DEVELOPMENT_WORKFLOW.md     # 🚧 Планируется
├── TESTING.md                  # 🚧 Планируется
├── CODE_REVIEW.md              # 🚧 Планируется
├── TROUBLESHOOTING.md          # 🚧 Планируется
└── SECURITY.md                 # 🚧 Планируется
```

---

## 📝 Примечания

### Легенда статусов
- ✅ **Готов** - гайд полностью написан и проверен
- 🚧 **Планируется** - гайд в планах, структура согласована
- 🔄 **В работе** - гайд активно пишется
- 📝 **На ревью** - гайд написан, проходит проверку

### Как использовать гайды
1. **Новичкам** - следуйте рекомендуемым трекам обучения
2. **Опытным** - используйте как reference материал
3. **Контрибьюторам** - обязательно изучите Development Workflow и Code Review

### Как дополнить гайды
- Создайте Issue с предложением улучшения
- Создайте PR с дополнениями
- Следуйте формату существующих гайдов
- Используйте Mermaid для диаграмм

---

## 🔗 Связанная документация

### Основная документация (корень проекта)
- [`README.md`](../../README.md) - Быстрый старт и основная информация
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) - Правила контрибуции
- [`CHANGELOG.md`](../../CHANGELOG.md) - История изменений

### Техническая документация (docs/)
- [`vision.md`](../vision.md) - Техническое видение проекта
- [`tasklist.md`](../tasklist.md) - План разработки MVP
- [`techDebtTasklist.md`](../techDebtTasklist.md) - Технический долг
- [`FALLBACK.md`](../FALLBACK.md) - Fallback механизм

### Правила разработки (.cursor/rules/)
- `conventions.mdc` - Coding conventions
- `qa_conventions.mdc` - QA стандарты
- `workflow.mdc` - TDD workflow

---

## 💬 Обратная связь

Нашли ошибку или хотите улучшить гайд?
- Создайте [Issue](https://github.com/jewishcoder/ai-tg-bot/issues)
- Предложите [Pull Request](https://github.com/jewishcoder/ai-tg-bot/pulls)

---

**Версия:** 1.0  
**Последнее обновление:** 2025-10-16  
**Статус проекта:** 🏆 Production-ready (MVP)

