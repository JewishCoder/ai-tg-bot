# Configuration Files

Этот каталог содержит конфигурационные файлы приложения.

## Файлы

- **site.ts** - Конфигурация сайта (название, описание, ссылки)
- **api.ts** - Конфигурация API (baseUrl, endpoints, timeout)

## Использование

```typescript
import { siteConfig } from '@/config/site'
import { apiConfig } from '@/config/api'
```

## Принципы

- Все конфигурации типизированы
- Environment variables через process.env.NEXT_PUBLIC_*
- Значения по умолчанию для development
- Не содержат секреты (используйте .env.local)

