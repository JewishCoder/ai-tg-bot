# AI Telegram Bot Dashboard - Frontend

Web-интерфейс для мониторинга статистики диалогов AI Telegram бота.

## 📦 Версия

**Текущая версия**: `0.1.0` (см. [VERSION](./VERSION))

### Схема версионирования (SemVer)

Проект использует [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR.MINOR.PATCH** (например: `0.1.0`)
- **MAJOR**: Breaking changes (несовместимые изменения API)
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Bug fixes (обратно совместимые исправления)

## 🛠️ Tech Stack

| Компонент | Технология | Версия | Обоснование |
|-----------|------------|--------|-------------|
| **Framework** | Next.js (App Router) | 15.5.6 | SSR/SSG, оптимизация производительности, современный роутинг |
| **Language** | TypeScript | 5+ | Строгая типизация, безопасность кода |
| **UI Library** | shadcn/ui | latest | Современные компоненты, Radix UI, полная кастомизация |
| **Styling** | Tailwind CSS | 4+ | Utility-first CSS, быстрая разработка, минимальный bundle |
| **Package Manager** | npm | latest | Стабильность, совместимость с Windows |
| **State Management** | TanStack Query (React Query) | latest | Кеширование, автоматический refetch, optimistic updates |
| **Data Fetching** | Axios | latest | Типизированные HTTP запросы |
| **Testing** | Vitest + Testing Library | latest | Быстрое тестирование, совместимость с Jest |
| **Linter** | ESLint + TypeScript ESLint | latest | Проверка качества кода |
| **Formatter** | Prettier | latest | Единый стиль кода |

## 📋 Prerequisites

- Node.js >= 18.17.0
- npm >= 8.0.0

## 🚀 Getting Started

### Установка зависимостей

```bash
npm install
```

### Разработка

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📜 Available Scripts

| Script | Описание |
|--------|----------|
| `npm run dev` | Запуск dev сервера с hot-reload |
| `npm run build` | Сборка для production |
| `npm run start` | Запуск production сервера |
| `npm run lint` | Проверка ESLint |
| `npm run format` | Форматирование кода через Prettier |
| `npm run format:check` | Проверка форматирования |
| `npm run type-check` | Проверка TypeScript типов |
| `npm run test` | Запуск тестов (watch mode) |
| `npm run test:ui` | Запуск тестов с UI |
| `npm run test:coverage` | Запуск тестов с coverage |

### Makefile Commands (из корня проекта)

```bash
make frontend-install        # Установка зависимостей
make frontend-dev            # Запуск dev сервера
make frontend-build          # Production build
make frontend-lint           # Lint проверка
make frontend-format         # Форматирование кода
make frontend-type-check     # Проверка типов
make frontend-test           # Запуск тестов
make frontend-check          # Все проверки (lint + type-check + test)
make frontend-clean          # Очистка build файлов
```

## 📁 Project Structure

```
frontend/
├── app/                       # Next.js App Router
│   ├── layout.tsx            # Root layout с Header, Footer
│   ├── page.tsx              # Home page (Dashboard)
│   ├── providers.tsx         # React Query Provider
│   └── globals.css           # Global styles + Tailwind
├── components/
│   ├── ui/                   # shadcn/ui components (10+ компонентов)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/               # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── README.md
│   ├── dashboard/            # Dashboard specific components (будущее)
│   └── common/               # Reusable common components (будущее)
├── lib/
│   ├── utils.ts              # Utility functions (cn, etc)
│   ├── api.ts                # API client (Axios)
│   └── hooks/
│       └── useStats.ts       # Custom React Query hook
├── types/
│   ├── index.d.ts            # Global types
│   └── api.ts                # API types (StatsResponse, Period, etc)
├── config/
│   ├── site.ts               # Site configuration
│   └── api.ts                # API configuration
├── public/                   # Static files
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── setup.ts              # Test setup
├── .husky/                   # Git hooks
│   └── pre-commit            # Pre-commit hook
├── .eslintrc.json            # ESLint config
├── .prettierrc               # Prettier config
├── tsconfig.json             # TypeScript config (strict mode)
├── next.config.ts            # Next.js config
├── tailwind.config.ts        # Tailwind config
├── components.json           # shadcn/ui config
├── vitest.config.ts          # Vitest config
├── package.json              # Dependencies и scripts
├── Dockerfile                # Docker config
└── README.md                 # This file
```

## 🎨 Styling

### Tailwind CSS

Проект использует Tailwind CSS 4 для стилизации:

- Utility-first подход
- Responsive design по умолчанию
- Dark/Light mode support
- Custom color palette (Slate)

### shadcn/ui

Установлены следующие компоненты:

- Button
- Card
- Table
- Tabs
- Badge
- Skeleton
- Sonner (Toasts)
- Dialog
- Dropdown Menu
- Select

Добавление новых компонентов:

```bash
npx shadcn@latest add <component-name>
```

## 🔌 API Integration

### Configuration

API настраивается через environment variables:

```env
# .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### API Client

Типизированный API client с автоматическим retry и error handling:

```typescript
import { apiClient } from '@/lib/api'

// Get stats
const stats = await apiClient.getStats('day')

// Health check
const health = await apiClient.healthCheck()
```

### React Query Hooks

```typescript
import { useStats } from '@/lib/hooks/useStats'

function DashboardPage() {
  const { data, isLoading, error } = useStats('day')
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error!</div>
  
  return <div>{data.summary.total_dialogs}</div>
}
```

## 🧪 Testing

### Running Tests

```bash
# Run tests (watch mode)
npm run test

# Run tests once
npm run test -- --run

# Run with coverage
npm run test:coverage
```

### Writing Tests

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

describe('Component', () => {
  it('should render', () => {
    render(<Component />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## 🐳 Docker

### Build Docker Image

```bash
cd frontend
docker build -t ai-tg-bot-frontend .
```

### Run in Docker

```bash
docker run -p 3000:3000 ai-tg-bot-frontend
```

### docker-compose

```bash
# From project root
docker-compose up frontend
```

## 📝 Code Standards

### Naming Conventions

- **React Components**: `PascalCase.tsx` (e.g., `DashboardCard.tsx`)
- **Utilities/Hooks**: `camelCase.ts` (e.g., `useStats.ts`)
- **Types**: `camelCase.ts` (e.g., `api.ts`)
- **Constants**: `UPPER_SNAKE_CASE`

### TypeScript

- Strict mode enabled
- Type hints обязательны
- No `any` without justification
- Use interfaces for objects

### React Patterns

- Functional components with hooks
- Use `use client` для client components
- Server components по умолчанию
- Composition over inheritance

### Styling

- Use Tailwind utility classes
- Use `cn()` helper for combining classes
- Mobile-first responsive design
- Follow shadcn/ui patterns

## 🔧 Development Tools

### Pre-commit Hooks

Pre-commit hooks автоматически:

- Форматируют код (Prettier)
- Проверяют lint (ESLint)
- Проверяют типы (TypeScript)

### VS Code Extensions (Recommended)

- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Hero
- Error Lens

### VS Code Settings

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## 🎯 Future Development

Следующие спринты добавят:

- Dashboard страницу с реальной статистикой
- Stats Cards компоненты
- Activity Timeline график
- Recent Dialogs таблица
- Top Users таблица
- Responsive design для mobile
- Dark mode support
- Real-time updates
- Error boundaries
- Loading states

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Docs](https://ui.shadcn.com/)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Vitest Docs](https://vitest.dev/)

## 🤝 Contributing

См. [CONTRIBUTING.md](../CONTRIBUTING.md) в корне проекта.

## 📄 License

MIT License - см. [LICENSE](../LICENSE) файл.
