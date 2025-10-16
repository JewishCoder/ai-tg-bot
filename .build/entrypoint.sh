#!/bin/sh
# Entrypoint script для production контейнера
# Исправляет права доступа к volume-директориям

set -e

echo "🚀 Starting AI Telegram Bot..."

# Проверка обязательных переменных окружения
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "❌ ERROR: TELEGRAM_TOKEN environment variable is not set"
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ ERROR: DB_PASSWORD environment variable is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Создание директорий если их нет
mkdir -p /app/data /app/logs /app/.cache

# Исправление прав доступа для volume-директорий
echo "🔧 Setting up directories permissions..."
echo "   Current user: $(id)"

# Изменяем владельца на пользователя bot
if chown -R bot:bot /app/data /app/logs /app/.cache 2>&1; then
    echo "   ✓ Owner changed to bot:bot"
else
    echo "   ⚠ Warning: Could not change owner (running as non-root?)"
fi

# Устанавливаем права на запись
if chmod -R 777 /app/data /app/logs /app/.cache 2>&1; then
    echo "   ✓ Permissions set to 777"
else
    echo "   ⚠ Warning: Could not change permissions"
fi

# Проверка результата
echo "   Final permissions:"
ls -la /app/logs | head -3
echo ""

echo "✅ Directories ready"
echo "📁 Data dir: /app/data"
echo "📄 Logs dir: /app/logs"
echo ""

# Запуск миграций БД
echo "🗄️  Running database migrations..."
if uv run alembic upgrade head; then
    echo "✅ Database migrations completed"
else
    echo "❌ ERROR: Database migrations failed"
    exit 1
fi
echo ""

# Запуск основного приложения
echo "🤖 Launching bot..."
exec "$@"

