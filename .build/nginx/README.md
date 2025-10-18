# AI TG Bot - Nginx Reverse Proxy

Nginx конфигурация для reverse proxy между frontend и API.

## 📦 Версия

**Текущая версия**: `1.0.0` (см. [VERSION](./VERSION))

### Схема версионирования (SemVer)

Проект использует [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR.MINOR.PATCH** (например: `1.0.0`)
- **MAJOR**: Breaking changes (несовместимые изменения конфигурации)
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Bug fixes (обратно совместимые исправления)

## Конфигурация

Nginx настроен для:

- Проксирование запросов к API (`:8000`) на `/api`
- Проксирование запросов к Frontend (`:3000`) на `/`
- Health check endpoint на `/health`
- Gzip сжатие для статических файлов
- Оптимизированные настройки для production

## Endpoints

- `http://localhost:8081/` → Frontend (Next.js)
- `http://localhost:8081/api/` → API (FastAPI)
- `http://localhost:8081/health` → Health check

## Docker

### Запуск через docker-compose

```bash
# Из корня проекта
docker-compose up nginx
```

### Build Docker образа

```bash
docker build -t ai-tg-bot-nginx -f .build/nginx/Dockerfile .build/nginx
```

### Запуск контейнера

```bash
docker run -d \
  --name ai-tg-bot-nginx \
  -p 8081:80 \
  --network ai-tg-bot-network \
  ai-tg-bot-nginx
```

## Структура

```
.build/nginx/
├── VERSION           # Версия Nginx конфигурации
├── nginx.conf        # Nginx конфигурация
├── Dockerfile        # Docker образ (будет создан в Спринте S8)
└── README.md         # Этот файл
```

## Health Check

Nginx предоставляет health check endpoint:

```bash
curl http://localhost:8081/health
```

Ответ:

```json
{
  "status": "healthy",
  "service": "nginx"
}
```

## Производительность

Настройки оптимизированы для production:

- Gzip сжатие для статических файлов
- Кэширование headers
- Оптимизированные буферы
- Connection pooling для upstream серверов

## CI/CD

Nginx образ автоматически собирается и публикуется в Yandex Container Registry через GitHub Actions (Спринт S8).

### Docker образ

```
cr.yandex/<registry-id>/ai-tg-nginx:{version|latest}
```

## Связанные документы

- [docker-compose.yml](../../docker-compose.yml) - общая конфигурация сервисов
- [Roadmap](../../docs/roadmap.md) - план развития проекта
- [CI/CD Guide](../../docs/guides/ci-cd.md) - документация CI/CD (будет создана в Спринте S8)

