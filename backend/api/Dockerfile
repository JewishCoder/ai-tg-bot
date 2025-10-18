# Dockerfile для Stats API
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Установка uv для управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Копирование файлов проекта (из context ./backend)
COPY api/pyproject.toml .
COPY api/uv.lock .
COPY api/README.md .

# Установка зависимостей
RUN uv sync --frozen --no-dev

# Копирование исходного кода
COPY api/src/ ./src/
COPY api/run_api.py .

# Копирование shared models из Bot сервиса
COPY bot/src/models.py ./shared/models.py

# Создание non-root пользователя
RUN useradd -m -u 1000 apiuser && \
    chown -R apiuser:apiuser /app
USER apiuser

# Expose порт
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Запуск приложения
CMD ["uv", "run", "python", "run_api.py"]

