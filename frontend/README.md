# AI Telegram Bot Dashboard - Frontend

Web-интерфейс для мониторинга статистики диалогов AI Telegram бота.

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui
- **Package Manager**: npm

## 📋 Prerequisites

- Node.js >= 18.17.0
- npm >= 8.0.0

## 🚀 Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## 📜 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page (Dashboard)
│   └── globals.css        # Global styles + Tailwind
├── components/
│   └── ui/                # shadcn/ui components (10+ components)
├── lib/
│   └── utils.ts           # Utility functions (cn, etc)
├── types/
│   └── index.d.ts         # Global type definitions
├── public/                # Static files
├── components.json        # shadcn/ui configuration
├── tsconfig.json          # TypeScript configuration (strict mode)
├── package.json           # Dependencies and scripts
└── README.md
```

## 📚 Documentation

- [Technical Vision](../docs/frontend/front-vision.md) - Полное техническое видение frontend
- [Dashboard Requirements](../docs/frontend/dashboard-requirements.md) - Требования к дашборду
- [API Contract](../docs/backend/api/stats-api-contract.md) - REST API контракт

## 🎨 UI Components

Проект использует [shadcn/ui](https://ui.shadcn.com/) - коллекцию переиспользуемых компонентов построенных на Radix UI и Tailwind CSS.

Установленные компоненты:
- Button
- Card
- Table
- Tabs
- Badge
- Skeleton
- Dialog
- Dropdown Menu
- Select
- Sonner (Toast notifications)

## 🔧 Development

### TypeScript

Проект использует строгий режим TypeScript со всеми дополнительными проверками:
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noImplicitReturns: true`
- `noUncheckedIndexedAccess: true`

### Styling

Tailwind CSS 4 с CSS variables для тем (light/dark mode).

### Code Quality

- ESLint для проверки качества кода
- TypeScript strict mode для типобезопасности
- Prettier для форматирования (будет добавлен в следующих блоках)

## 🚀 Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📝 Status

**Sprint S4 - Block 2**: ✅ Completed
- Next.js 15 project initialized
- TypeScript strict mode configured
- shadcn/ui integrated with 10+ components
- Production build successful

**Next Steps**: Block 3 - Project Structure and Configuration

---

Для дополнительной информации см. [docs/roadmap.md](../docs/roadmap.md)
