# CI/CD Guide - AI Telegram Bot

Полная документация по CI/CD процессам проекта AI Telegram Bot.

## 📋 Содержание

- [Обзор архитектуры](#обзор-архитектуры)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Версионирование](#версионирование)
- [Docker Registry](#docker-registry)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Обзор архитектуры

Проект использует multi-service архитектуру с отдельными CI/CD pipelines для каждого сервиса:

- **Bot** (`backend/bot`) - Telegram бот на Python
- **API** (`backend/api`) - REST API на FastAPI
- **Frontend** (`frontend`) - Next.js 15 веб-приложение
- **Nginx** (`.build/nginx`) - Reverse proxy

### Схема CI/CD

```text
┌─────────────────┐
│  Git Push/PR    │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │
         v                  v                  v                  v
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   CI - Bot     │  │   CI - API     │  │  CI - Frontend │  │  CI - Nginx    │
│                │  │                │  │                │  │                │
│ • Lint/Format  │  │ • Lint/Format  │  │ • Lint/Format  │  │ • Config Test  │
│ • Type Check   │  │ • Type Check   │  │ • Type Check   │  │                │
│ • Tests (80%)  │  │ • Tests (70%)  │  │ • Tests (80%)  │  │                │
│                │  │ • Integration  │  │ • Build Check  │  │                │
└────────┬───────┘  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
         │                  │                  │                  │
         │ (main only)      │ (main only)      │ (main only)      │ (main only)
         v                  v                  v                  v
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Docker Build & │  │ Docker Build & │  │ Docker Build & │  │ Docker Build & │
│ Push to        │  │ Push to        │  │ Push to        │  │ Push to        │
│ Registry       │  │ Registry       │  │ Registry       │  │ Registry       │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

---

## GitHub Actions Workflows

### Структура workflows

```text
.github/workflows/
├── ci-bot.yml          # Bot CI/CD
├── ci-api.yml          # API CI/CD  
├── ci-frontend.yml     # Frontend CI/CD
└── ci-nginx.yml        # Nginx CI/CD
```

### Общие характеристики

Все workflows имеют:

- ✅ **Triggers**: push и PR для `main`, `develop` веток
- ✅ **Path filters**: запускаются только при изменении релевантных файлов
- ✅ **Concurrency groups**: автоматическая отмена устаревших сборок
- ✅ **Caching**: кэширование зависимостей (uv, npm, docker layers)
- ✅ **Conditional push**: Docker образы публикуются только для `main` ветки

---

### CI - Bot Workflow

**Файл**: `.github/workflows/ci-bot.yml`

**Триггеры**:
- Push/PR на `main`, `develop`
- Изменения в `backend/bot/**`, `.build/Dockerfile`, `.github/workflows/ci-bot.yml`

**Jobs**:

1. **bot-quality** - Проверка качества кода
   - Python 3.11 + uv
   - Ruff format check
   - Ruff lint
   - Mypy type check
   - Pytest с coverage >= 80%

2. **bot-docker** - Сборка и публикация Docker образа
   - Зависит от: `bot-quality`
   - Условие: только push в `main`
   - Читает версию из `backend/bot/VERSION`
   - Build с Docker Buildx
   - Push в Yandex Container Registry
   - Теги: `{version}` и `latest`

**Секреты**:
- `YA_CLOUD_REGISTRY` - JSON ключ для доступа к registry
- `YC_REGISTRY_ID` - ID registry в Yandex Cloud

---

### CI - API Workflow

**Файл**: `.github/workflows/ci-api.yml`

**Триггеры**:
- Push/PR на `main`, `develop`
- Изменения в `backend/api/**`, `.github/workflows/ci-api.yml`

**Jobs**:

1. **api-quality** - Проверка качества кода
   - Python 3.11 + uv
   - Ruff format check
   - Ruff lint
   - Mypy type check
   - Pytest unit-tests с coverage >= 70%

2. **api-integration-tests** - Интеграционные тесты
   - PostgreSQL 16 service container
   - Environment variables для DB подключения
   - Pytest integration tests (`-m integration`)

3. **api-docker** - Сборка и публикация Docker образа
   - Зависит от: `api-quality`, `api-integration-tests`
   - Условие: только push в `main`
   - Читает версию из `backend/api/VERSION`
   - Push в Yandex Container Registry

---

### CI - Frontend Workflow

**Файл**: `.github/workflows/ci-frontend.yml`

**Триггеры**:
- Push/PR на `main`, `develop`
- Изменения в `frontend/**`, `.github/workflows/ci-frontend.yml`

**Jobs**:

1. **frontend-quality** - Проверка качества кода
   - Node.js 20
   - npm ci (с кэшированием)
   - ESLint
   - Prettier format check
   - TypeScript type check (`tsc --noEmit`)
   - Vitest с coverage >= 80%
   - Next.js build check

2. **frontend-docker** - Сборка и публикация Docker образа
   - Зависит от: `frontend-quality`
   - Условие: только push в `main`
   - Читает версию из `frontend/VERSION`
   - Push в Yandex Container Registry

---

### CI - Nginx Workflow

**Файл**: `.github/workflows/ci-nginx.yml`

**Триггеры**:
- Push/PR на `main`, `develop`
- Изменения в `.build/nginx/**`, `.github/workflows/ci-nginx.yml`

**Jobs**:

1. **nginx-validate** - Валидация конфигурации
   - Тест nginx конфигурации (`nginx -t`)

2. **nginx-docker** - Сборка и публикация Docker образа
   - Зависит от: `nginx-validate`
   - Условие: только push в `main`
   - Читает версию из `.build/nginx/VERSION`
   - Push в Yandex Container Registry

---

## Версионирование

### Semantic Versioning (SemVer)

Все сервисы используют [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (несовместимые изменения API)
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Bug fixes (обратно совместимые исправления)

### VERSION файлы

Каждый сервис имеет свой VERSION файл:

- `backend/bot/VERSION` - версия бота (текущая: `1.4.2`)
- `backend/api/VERSION` - версия API (текущая: `0.1.0`)
- `frontend/VERSION` - версия frontend (текущая: `0.1.0`)
- `.build/nginx/VERSION` - версия nginx (текущая: `1.0.0`)

**Формат файла**:
```
0.1.0
```

Только версия без лишних символов и newline в конце.

### Обновление версии

1. Определите тип изменений (MAJOR/MINOR/PATCH)
2. Обновите VERSION файл сервиса
3. Закоммитьте изменения:

```bash
git add backend/api/VERSION
git commit -m "chore: bump API version to 0.2.0"
```

4. Push в `main` ветку запустит автоматическую сборку с новой версией

---

## Docker Registry

### Yandex Container Registry

Все Docker образы публикуются в Yandex Container Registry.

**Registry URL**: `cr.yandex/<registry-id>`

### Образы

```text
cr.yandex/<registry-id>/ai-tg-bot:{version|latest}        # Bot
cr.yandex/<registry-id>/ai-tg-api:{version|latest}        # API
cr.yandex/<registry-id>/ai-tg-frontend:{version|latest}   # Frontend
cr.yandex/<registry-id>/ai-tg-nginx:{version|latest}      # Nginx
```

### Теги

- `{version}` - конкретная версия из VERSION файла (например: `0.1.0`)
- `latest` - последняя собранная версия

**Рекомендация**: Для production используйте конкретные версии, а не `latest`.

### Настройка секретов

В GitHub настройте секреты:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте секреты:
   - `YA_CLOUD_REGISTRY` - JSON ключ для доступа к registry
   - `YC_REGISTRY_ID` - ID вашего registry

**Создание JSON ключа**:

```bash
# Создайте service account
yc iam service-account create --name github-actions

# Назначьте роль
yc container registry add-access-binding <registry-id> \
  --service-account-name github-actions \
  --role container-registry.images.pusher

# Создайте JSON ключ
yc iam key create --service-account-name github-actions \
  --output key.json

# Скопируйте содержимое key.json в GitHub секрет YA_CLOUD_REGISTRY
```

---

## Production Deployment

### Режимы работы

#### Development Mode (локальная сборка)

```bash
# docker-compose.yml использует 'build' директивы
docker-compose up -d
```

Образы собираются локально из исходников.

#### Production Mode (образы из registry)

1. Отредактируйте `docker-compose.yml`:

```yaml
# Закомментируйте 'build' секции
# build:
#   context: ./backend/bot
#   dockerfile: Dockerfile.dev

# Раскомментируйте 'image' директивы
image: cr.yandex/${YC_REGISTRY_ID}/ai-tg-bot:${BOT_VERSION:-latest}
```

2. Создайте `.env.production`:

```bash
cp .env.production.example .env.production
# Отредактируйте значения
```

3. Деплой:

```bash
make pull-images   # Скачать образы из registry
make deploy-prod   # Запустить production
```

### Makefile команды

```bash
# Production deployment
make pull-images              # Pull Docker images from registry
make deploy-prod              # Deploy production environment
make restart-service service=api  # Restart specific service
make prod-logs                # View all production logs
make prod-status              # Show production services status
```

### Переменные окружения

**Development** (`.env.development`):
- Локальные значения
- Используется для разработки

**Production** (`.env.production`):
- Production значения
- Секреты и credentials
- Конкретные версии образов

**Пример `.env.production`**:

```env
YC_REGISTRY_ID=your-registry-id

# Конкретные версии
BOT_VERSION=1.4.2
API_VERSION=0.1.0
FRONTEND_VERSION=0.1.0
NGINX_VERSION=1.0.0

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ai_tg_bot
DB_USER=botuser
DB_PASSWORD=your-secure-password

# Secrets
TELEGRAM_BOT_TOKEN=your-token
OPENROUTER_API_KEY=your-api-key
```

---

## Troubleshooting

### Проблема: GitHub Actions не запускаются

**Причина**: Path filters не совпадают с измененными файлами.

**Решение**: Проверьте что ваши изменения соответствуют path filters в workflow:

```yaml
on:
  push:
    paths:
      - 'backend/api/**'  # Запускается только при изменениях в backend/api/
```

### Проблема: Docker build fails в GitHub Actions

**Причина**: Секреты не настроены или неверны.

**Решение**:
1. Проверьте что секреты `YA_CLOUD_REGISTRY` и `YC_REGISTRY_ID` настроены
2. Убедитесь что JSON ключ валиден
3. Проверьте права service account

### Проблема: Tests fail в CI

**Причина**: Coverage ниже порога или тесты падают.

**Решение**:
1. Запустите тесты локально:
   ```bash
   # Bot
   cd backend/bot
   uv run pytest tests/ --cov=src --cov-report=term
   
   # API
   cd backend/api
   uv run pytest tests/ --cov=src --cov-report=term
   
   # Frontend
   cd frontend
   npm test -- --coverage
   ```

2. Исправьте падающие тесты
3. Добавьте недостающие тесты для покрытия

### Проблема: Docker image не публикуется

**Причина**: Условие `if: github.ref == 'refs/heads/main'` не выполняется.

**Решение**: Docker образы публикуются только при push в `main` ветку. Для PR они не публикуются (это ожидаемое поведение).

### Проблема: Version читается неправильно

**Причина**: VERSION файл содержит лишние символы.

**Решение**: Убедитесь что VERSION файл содержит только версию:

```bash
echo -n "0.1.0" > backend/api/VERSION
```

Без newline в конце!

### Проблема: Integration tests fail в API

**Причина**: PostgreSQL service container не готов или неверные credentials.

**Решение**: Проверьте что environment variables правильно настроены в workflow:

```yaml
env:
  DB_HOST: localhost
  DB_PORT: 5432
  DB_NAME: testdb
  DB_USER: testuser
  DB_PASSWORD: testpassword
```

### Проблема: Production deployment fails

**Причина**: Образы не найдены в registry или неверные credentials.

**Решение**:
1. Проверьте что образы существуют в registry:
   ```bash
   yc container image list --registry-id <registry-id>
   ```

2. Проверьте `.env.production` файл
3. Убедитесь что используете правильные версии

### Проблема: Cache не работает

**Причина**: Cache key изменился или cache был очищен.

**Решение**: 
- Для uv: cache зависит от `pyproject.toml`
- Для npm: cache зависит от `package-lock.json`
- Для docker: используется GitHub Actions cache (type=gha)

При изменении зависимостей cache автоматически обновится.

---

## Best Practices

### 1. Версионирование

- ✅ Используйте конкретные версии для production
- ✅ Обновляйте VERSION файл при каждом релизе
- ✅ Следуйте SemVer правилам
- ❌ Не используйте `latest` в production

### 2. Git Workflow

- ✅ Разрабатывайте в feature branches
- ✅ Создавайте PR для review
- ✅ Мердж в `develop` для staging
- ✅ Мердж в `main` для production
- ❌ Не коммитьте напрямую в `main`

### 3. Docker Images

- ✅ Проверяйте размер образов
- ✅ Используйте multi-stage builds где возможно
- ✅ Минимизируйте количество layers
- ✅ Используйте `.dockerignore`
- ❌ Не включайте секреты в образы

### 4. Testing

- ✅ Пишите тесты для новой функциональности
- ✅ Поддерживайте coverage >= порога
- ✅ Запускайте тесты локально перед push
- ✅ Используйте fixtures для повторяющихся данных
- ❌ Не игнорируйте падающие тесты

### 5. CI/CD

- ✅ Используйте path filters для оптимизации
- ✅ Кэшируйте зависимости
- ✅ Настройте concurrency groups
- ✅ Мониторьте время выполнения workflows
- ❌ Не публикуйте секреты в логах

---

## Метрики и мониторинг

### CI/CD Метрики

- **Build Time**: < 10 минут для полного pipeline
- **Success Rate**: > 95% успешных сборок
- **Coverage**: Bot >= 80%, API >= 70%, Frontend >= 80%

### Мониторинг

- GitHub Actions dashboard: мониторинг успешности workflows
- Container Registry: мониторинг размеров образов
- Production logs: `make prod-logs`
- Services status: `make prod-status`

---

## Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Semantic Versioning](https://semver.org/)
- [Yandex Cloud Container Registry](https://cloud.yandex.ru/docs/container-registry/)
- [Project Roadmap](../roadmap.md)
- [Sprint S8 Tasklist](../tasklists/tasklist-S8.md)

---

**Последнее обновление**: 2025-10-18  
**Версия документа**: 1.0.0

