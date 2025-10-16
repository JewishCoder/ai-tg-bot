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

# Создание БД если её нет
echo "🗄️  Checking database existence..."
export PGPASSWORD="${DB_PASSWORD}"
DB_EXISTS=$(psql -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-botuser}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME:-ai_tg_bot}'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" = "1" ]; then
    echo "✅ Database '${DB_NAME:-ai_tg_bot}' already exists"
else
    echo "📦 Creating database '${DB_NAME:-ai_tg_bot}'..."
    if psql -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-botuser}" -d postgres -c "CREATE DATABASE ${DB_NAME:-ai_tg_bot};" 2>/dev/null; then
        echo "✅ Database created successfully"
    else
        echo "⚠️  Warning: Could not create database (might already exist or insufficient permissions)"
        echo "   Please create database manually:"
        echo "   CREATE DATABASE ${DB_NAME:-ai_tg_bot};"
    fi
fi
unset PGPASSWORD
echo ""

# Запуск миграций БД
echo "🗄️  Running database migrations..."
if uv run alembic upgrade head; then
    echo "✅ Database migrations completed"
else
    echo "❌ ERROR: Database migrations failed"
    echo "   Please check that database exists and credentials are correct"
    exit 1
fi
echo ""

# Запуск основного приложения
echo "🤖 Launching bot..."
exec "$@"

