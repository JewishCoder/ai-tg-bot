# Changelog

Все значимые изменения в проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- 🛡️ **Fallback механизм для повышения надежности**
  - Автоматическое переключение на резервную LLM модель при недоступности основной
  - Поддержка `OPENROUTER_FALLBACK_MODEL` в конфигурации
  - Умное определение когда нужен fallback (Rate Limit, API Errors)
  - Retry механизм для fallback модели (3 попытки)
  - Логирование всех fallback операций с уровнем WARNING
  - Полная прозрачность для пользователя (не видят технических деталей)
- 📖 Документация fallback механизма (`docs/FALLBACK.md`)
- 🧪 Интеграционные тесты для fallback флоу (5 новых тестов)
- 📊 Coverage увеличен до 85% (с 80%)

### Changed
- ⚡ `LLMClient` теперь поддерживает fallback модель
- 📝 Обновлен `README.md` с описанием fallback функционала
- 🎯 Обновлены `docs/idea.md` и `docs/vision.md` с fallback спецификацией

### Technical Details
- Новые методы в `LLMClient`:
  - `_should_try_fallback(error)` - определяет нужен ли fallback
  - `_try_fallback_model(messages, user_id, error)` - выполняет fallback запрос
- Интеграция fallback в `generate_response()` для RateLimitError и APIError
- Fallback НЕ срабатывает для Timeout и Connection ошибок (проблема сети)
- Полная обратная совместимость - fallback опционален

### Tests
- ✅ 4 новых unit-теста для Config (fallback model)
- ✅ 7 новых unit-тестов для LLMClient (fallback логика)
- ✅ 5 новых интеграционных тестов (end-to-end fallback флоу)
- ✅ Всего 65 тестов (coverage 85%)

## [0.1.0] - 2025-10-11

### Added
- 🤖 Базовая функциональность Telegram бота
- 🧠 Интеграция с OpenRouter API для LLM
- 💾 Управление историей диалогов (Storage)
- 🎭 Система ролей через системный промпт
- 🔄 Retry механизм для временных сбоев
- 📝 Логирование всех операций
- 🐳 Docker support с development и production сборками
- 🧪 Unit и интеграционные тесты (coverage 80%)
- 📚 Документация (README, CONTRIBUTING, docs/)
- 🔧 CI/CD через GitHub Actions
- 🚀 Автоматическая публикация в Yandex Container Registry

### Commands
- `/start` - начать работу с ботом
- `/help` - справка по командам
- `/role <текст>` - установить роль ассистента
- `/role default` - вернуться к роли по умолчанию
- `/reset` - очистить историю диалога
- `/status` - показать статус и статистику

### Tech Stack
- Python 3.11+
- aiogram 3.x - Telegram Bot API
- OpenAI SDK - для работы с OpenRouter
- Pydantic - валидация конфигурации
- uv - управление зависимостями
- Docker - контейнеризация
- Pytest - тестирование

---

## Типы изменений

- `Added` - новые функции
- `Changed` - изменения в существующем функционале
- `Deprecated` - функции, которые скоро будут удалены
- `Removed` - удаленные функции
- `Fixed` - исправления багов
- `Security` - изменения безопасности

---

[Unreleased]: https://github.com/jewishcoder/ai-tg-bot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jewishcoder/ai-tg-bot/releases/tag/v0.1.0

