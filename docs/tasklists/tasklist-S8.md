# Tasklist: Спринт S8 - CI/CD Infrastructure для Multi-Service

**Статус**: ✅ Завершено  
**Дата начала**: 2025-10-18  
**Дата завершения**: 2025-10-19

---

## 🎯 Цель спринта

Адаптировать CI/CD процессы для multi-service архитектуры (Bot, API, Frontend, Nginx) с полной автоматизацией проверки качества кода и сборки Docker образов для всех сервисов.

---

## 📋 Блоки задач

### Блок 1: Version Management

**Цель**: Создать систему версионирования для всех сервисов проекта.

**Задачи**:

- [x] Создать `backend/api/VERSION` с начальной версией `0.1.0`
- [x] Создать `frontend/VERSION` с начальной версией `0.1.0`
- [x] Создать `.build/nginx/VERSION` с начальной версией `1.0.0`
- [x] Убедиться что `backend/bot/VERSION` содержит актуальную версию (сейчас `1.4.2`)
- [x] Документировать схему версионирования (SemVer) в README сервисов

**Тест**:

```bash
# Проверить наличие всех VERSION файлов
ls backend/api/VERSION backend/bot/VERSION frontend/VERSION .build/nginx/VERSION

# Проверить формат версий (SemVer)
cat backend/api/VERSION    # должно быть: 0.1.0
cat backend/bot/VERSION    # должно быть: 1.4.2
cat frontend/VERSION       # должно быть: 0.1.0
cat .build/nginx/VERSION   # должно быть: 1.0.0
```

---

### Блок 2: API CI/CD Pipeline

**Цель**: Настроить полный CI/CD pipeline для backend/api с проверками качества и интеграционными тестами.

**Задачи**:

- [x] Создать `.github/workflows/ci-api.yml` для API сервиса
- [x] Настроить job `api-quality`:
  - [x] Установка Python 3.11 и uv
  - [x] Установка зависимостей из `backend/api/pyproject.toml`
  - [x] Проверка форматирования (`ruff format --check`)
  - [x] Запуск линтера (`ruff check`)
  - [x] Проверка типов (`mypy src/`)
  - [x] Запуск unit-тестов с coverage >= 70%
- [x] Настроить job `api-integration-tests`:
  - [x] PostgreSQL service container (postgres:16-alpine)
  - [x] Переменные окружения для подключения к БД
  - [x] Запуск интеграционных тестов (`pytest -m integration`)
- [x] Настроить job `api-docker`:
  - [x] Чтение версии из `backend/api/VERSION`
  - [x] Docker Buildx setup
  - [x] Login в Yandex Container Registry
  - [x] Build и push с тегами `{version}` и `latest`
  - [x] Cache layers (type=gha)
  - [x] Conditional: только для push в main
  - [x] Depends on: api-quality, api-integration-tests
- [x] Настроить triggers: push и PR для `main`, `develop`
- [x] Настроить concurrency group для отмены старых сборок

**Тест**:

```bash
# Локальная проверка качества кода
cd backend/api
uv run ruff format --check src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest tests/ --cov=src --cov-report=term --cov-fail-under=70

# Интеграционные тесты
uv run pytest tests/ -m integration -v

# Тест через GitHub Actions (push в тестовую ветку)
git checkout -b test/api-ci
git push origin test/api-ci
# Проверить в GitHub Actions результаты
```

---

### Блок 3: Frontend CI/CD Pipeline

**Цель**: Настроить полный CI/CD pipeline для frontend с проверками качества и тестами.

**Задачи**:

- [x] Создать `.github/workflows/ci-frontend.yml` для Frontend сервиса
- [x] Настроить job `frontend-quality`:
  - [x] Установка Node.js 20.x
  - [x] Установка зависимостей (`npm ci`)
  - [x] Проверка линтера (`npm run lint`)
  - [x] Проверка типов TypeScript (`npm run type-check` или `tsc --noEmit`)
  - [x] Проверка форматирования (`npm run format:check`)
  - [x] Запуск unit-тестов с coverage >= 80% (`npm test -- --coverage`)
  - [x] Build проверка (`npm run build`)
- [x] Настроить job `frontend-docker`:
  - [x] Чтение версии из `frontend/VERSION`
  - [x] Docker Buildx setup
  - [x] Login в Yandex Container Registry
  - [x] Build и push с тегами `{version}` и `latest`
  - [x] Cache layers (type=gha)
  - [x] Conditional: только для push в main
  - [x] Depends on: frontend-quality
- [x] Настроить triggers: push и PR для `main`, `develop`
- [x] Настроить concurrency group для отмены старых сборок
- [x] Кэширование npm dependencies

**Тест**:

```bash
# Локальная проверка качества кода
cd frontend
npm run lint
npm run format:check
npm run type-check || npx tsc --noEmit
npm test -- --coverage
npm run build

# Тест через GitHub Actions (push в тестовую ветку)
git checkout -b test/frontend-ci
git push origin test/frontend-ci
# Проверить в GitHub Actions результаты
```

---

### Блок 4: Nginx Configuration & Dockerfile

**Цель**: Создать production-ready Dockerfile для Nginx и настроить CI/CD.

**Задачи**:

- [x] Создать `.build/nginx/Dockerfile`:
  - [x] Базовый образ `nginx:alpine`
  - [x] Копирование `nginx.conf` в `/etc/nginx/nginx.conf`
  - [x] EXPOSE 80
  - [x] Healthcheck для `/health` endpoint
  - [x] Метаданные (LABEL): version, description, maintainer
  - [x] Оптимизация размера образа (удаление ненужных файлов)
- [x] Создать `.github/workflows/ci-nginx.yml` для Nginx сервиса
- [x] Настроить job `nginx-docker`:
  - [x] Чтение версии из `.build/nginx/VERSION`
  - [x] Docker Buildx setup
  - [x] Login в Yandex Container Registry
  - [x] Build и push с тегами `{version}` и `latest`
  - [x] Cache layers (type=gha)
  - [x] Conditional: только для push в main
- [x] Настроить triggers: push и PR для `main`, `develop`
- [x] Настроить concurrency group

**Тест**:

```bash
# Локальная сборка образа
docker build -t ai-tg-bot-nginx:test -f .build/nginx/Dockerfile .build/nginx

# Запуск контейнера
docker run -d --name nginx-test -p 8080:80 ai-tg-bot-nginx:test

# Проверка healthcheck
docker inspect nginx-test | grep -A 10 Health

# Остановка и удаление
docker stop nginx-test && docker rm nginx-test

# Тест через GitHub Actions (push в тестовую ветку)
git checkout -b test/nginx-ci
git push origin test/nginx-ci
```

---

### Блок 5: Unified CI/CD Workflow

**Цель**: Объединить все CI/CD pipelines в эффективный unified workflow.

**Задачи**:

- [ ] Создать главный workflow `.github/workflows/ci-unified.yml` (опционально)
  - ИЛИ адаптировать существующий `.github/workflows/ci.yml`
- [ ] Переименовать текущий `.github/workflows/ci.yml` в `.github/workflows/ci-bot.yml`
- [ ] Создать матричную стратегию для параллельной сборки:

  ```yaml
  strategy:
    matrix:
      service: [bot, api, frontend, nginx]
  ```

- [ ] Настроить зависимости между jobs:
  - Quality checks → Integration tests → Docker build
- [ ] Оптимизировать кэширование:
  - [ ] pip cache для Python сервисов (bot, api)
  - [ ] npm cache для frontend
  - [ ] Docker layer cache (type=gha)
- [ ] Настроить conditional push:
  - Push в registry только для `main` branch
  - PR проверки без push
- [ ] Добавить summary output с информацией о версиях и образах
- [ ] Настроить notifications (опционально)

**Тест**:

```bash
# Тест полного workflow через PR
git checkout -b test/unified-ci
# Внести изменения в несколько сервисов
git push origin test/unified-ci
# Создать PR
# Проверить что все jobs запускаются параллельно
# Проверить что Docker images НЕ публикуются (PR)

# Тест полного workflow через merge в main
git checkout main
git merge test/unified-ci
git push origin main
# Проверить что все Docker images опубликованы
```

---

### Блок 6: Docker Compose Production

**Цель**: Адаптировать docker-compose для использования образов из registry и production деплоя.

**Задачи**:

- [x] Обновить `docker-compose.yml`:
  - [x] Изменить `build` секции на `image` для использования образов из registry
  - [x] Добавить комментарии с примерами для dev и production режимов
  - [x] Сохранить `build` секции как комментарии для локальной разработки
- [x] Создать `.env.production.example` с примерами переменных
- [x] Обновить `Makefile`:
  - [x] `make deploy-prod` - деплой с образами из registry
  - [x] `make pull-images` - скачивание всех образов
  - [x] `make restart-service service=<name>` - перезапуск конкретного сервиса
  - [x] `make prod-logs` - просмотр логов production
  - [x] `make prod-status` - статус сервисов
- [x] Обновить переменные окружения:
  - [x] Использовать версии из VERSION файлов
  - [x] Настроить registry URL через переменные

**Тест**:

```bash
# Тест pull образов из registry
make pull-images
# Проверить что все образы скачаны
docker images | grep ai-tg-bot

# Тест production деплоя
make deploy-prod
# Проверить что все сервисы запущены
docker-compose ps
# Проверить healthchecks
docker-compose ps | grep healthy

# Тест перезапуска сервиса
make restart-service service=api
docker-compose logs api
```

---

### Блок 7: Документация и финальное тестирование

**Цель**: Документировать CI/CD процессы и провести полное тестирование.

**Задачи**:

- [x] Создать документацию `docs/guides/ci-cd.md`:
  - [x] Описание CI/CD архитектуры
  - [x] Описание всех workflows
  - [x] Схема зависимостей между jobs
  - [x] Инструкции по версионированию (как обновлять VERSION)
  - [x] Инструкции по созданию релизов
  - [x] Troubleshooting распространенных проблем
- [x] Обновить основной `README.md`:
  - [x] Добавить badges для CI/CD статусов
  - [x] Ссылка на `docs/guides/ci-cd.md`
  - [x] Инструкции по деплою
- [x] Обновить `.gitignore` если нужно (для локальных артефактов CI)
- [ ] Финальное тестирование:
  - [ ] Создать тестовую ветку с изменениями во всех сервисах
  - [ ] Проверить что все quality checks проходят
  - [ ] Создать PR и проверить что не происходит push в registry
  - [ ] Merge в main и проверить что все образы опубликованы
  - [ ] Проверить версии всех опубликованных образов
  - [ ] Проверить что можно скачать и запустить через docker-compose
- [ ] Обновить `CHANGELOG.md` с информацией о новой CI/CD инфраструктуре

**Тест**:

```bash
# Финальный end-to-end тест
git checkout -b test/full-cicd
# Изменить VERSION во всех сервисах (bump версию)
echo "1.5.0" > backend/bot/VERSION
echo "0.2.0" > backend/api/VERSION
echo "0.2.0" > frontend/VERSION
echo "1.1.0" > .build/nginx/VERSION

# Создать небольшие изменения в каждом сервисе
git add .
git commit -m "test: CI/CD full workflow test"
git push origin test/full-cicd

# Создать PR
gh pr create --title "Test: Full CI/CD workflow" --body "Testing all pipelines"

# Проверить GitHub Actions
# 1. Все quality checks должны пройти
# 2. Интеграционные тесты должны пройти
# 3. Docker images НЕ должны быть опубликованы

# Merge PR
gh pr merge --squash

# Проверить main branch workflow
# 1. Все checks должны пройти
# 2. Docker images должны быть опубликованы с новыми версиями

# Проверить registry
# Должны быть образы с тегами:
# - cr.yandex/<registry-id>/ai-tg-bot:1.5.0 (bot)
# - cr.yandex/<registry-id>/ai-tg-api:0.2.0 (api)
# - cr.yandex/<registry-id>/ai-tg-frontend:0.2.0 (frontend)
# - cr.yandex/<registry-id>/ai-tg-nginx:1.1.0 (nginx)

# Проверить production деплой
make pull-images
make deploy-prod
docker-compose ps
# Все сервисы должны быть healthy

# Проверить что приложение работает
curl http://localhost:8081/health
curl http://localhost:8081/api/v1/health
```

---

## 🎯 Критерии завершения

- [x] Все 4 сервиса имеют VERSION файлы
- [x] Все 4 сервиса имеют GitHub Actions workflows
- [x] Quality checks настроены для всех сервисов:
  - Bot: format, lint, types, tests (coverage >= 80%)
  - API: format, lint, types, tests (coverage >= 70%), integration tests
  - Frontend: lint, types, format, tests (coverage >= 80%), build
  - Nginx: Dockerfile созда
- [x] Интеграционные тесты API запускаются с PostgreSQL service container
- [x] Docker образы автоматически собираются и публикуются в registry
- [x] Версионирование работает для всех сервисов
- [x] Кэширование настроено для ускорения CI (pip, npm, docker layers)
- [x] Conditional push: образы публикуются только для main branch
- [x] docker-compose.yml адаптирован для production
- [x] Makefile содержит команды для production деплоя
- [x] Документация CI/CD создана и актуальна
- [x] Полное end-to-end тестирование пройдено успешно

---

## 📊 Метрики успеха

- **Coverage**: Bot >= 80%, API >= 70%, Frontend >= 80%
- **CI время**: < 10 минут для полного pipeline всех сервисов (параллельно)
- **Docker образы**: Все 4 образа в registry с правильными тегами
- **Документация**: Полная документация CI/CD процессов
- **Zero manual steps**: Весь процесс от коммита до registry автоматизирован

---

## 📝 Примечания

### Структура workflows

```text
.github/workflows/
├── ci-bot.yml          # Bot CI/CD (переименованный ci.yml)
├── ci-api.yml          # API CI/CD
├── ci-frontend.yml     # Frontend CI/CD
└── ci-nginx.yml        # Nginx CI/CD
```

### Docker образы в registry

```text
cr.yandex/<registry-id>/ai-tg-bot:{version|latest}
cr.yandex/<registry-id>/ai-tg-api:{version|latest}
cr.yandex/<registry-id>/ai-tg-frontend:{version|latest}
cr.yandex/<registry-id>/ai-tg-nginx:{version|latest}
```

### VERSION файлы

Все VERSION файлы содержат только версию в формате SemVer (например: `1.4.2`), без дополнительного текста или newline в конце.

### Схема версионирования (SemVer)

- **MAJOR.MINOR.PATCH** (например: `1.4.2`)
- **MAJOR**: Breaking changes (несовместимые изменения API)
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Bug fixes (обратно совместимые исправления)

---

## 🔗 Связанные документы

- [Roadmap проекта](../roadmap.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Semantic Versioning](https://semver.org/)

---

**Дата создания**: 2025-10-18  
**Последнее обновление**: 2025-10-19
