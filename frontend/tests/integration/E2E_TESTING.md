# 🧪 Автоматизированное тестирование Dashboard

## Установка

Playwright уже установлен в проекте. Убедитесь что установлены браузеры:

```bash
npx playwright install
```

## Доступные тесты

### 1. **Полное тестирование** (`test-dashboard.js`)

Запускает все тесты: светлая тема, темная тема, интерактивность, скриншоты.

```bash
node tests/integration/test-dashboard.js
```

**Что тестируется:**
- ✅ Загрузка страницы
- ✅ Отображение Header и компонентов
- ✅ 3 Summary Cards
- ✅ График активности
- ✅ Period Filter
- ✅ Sidebar сворачивание/разворачивание
- ✅ Переключение фильтров (День/Неделя/Месяц)
- ✅ Раскрытие таблиц (Последние диалоги, Топ пользователи)
- ✅ Переключение светлой/темной темы
- ✅ Проверка фона и цвета текста

**Результат:**
- Выводит отчет о пройденных/проваленных тестах
- Создает скриншоты: `dashboard-light-auto.png`, `dashboard-dark-auto.png`

---

### 2. **Быстрая проверка темы** (`test-dashboard-quick.js`)

Быстро проверяет работу темной темы.

```bash
node tests/integration/test-dashboard-quick.js
```

**Что проверяется:**
- Начальное состояние (светлая тема)
- Переключение на темную тему
- Наличие класса `.dark` на `<html>`
- Цвет фона и текста

**Результат:**
- Выводит состояние CSS переменных
- Показывает работает ли темная тема
- Создает скриншот: `dark-theme-check.png`

---

## Запуск перед коммитом

Рекомендуется запускать полное тестирование перед каждым коммитом:

```bash
# 1. Убедитесь что dev сервер запущен
npm run dev

# 2. В другом терминале запустите тесты (из папки frontend)
node tests/integration/test-dashboard.js
```

---

## Отладка

Если тесты падают:

1. **Убедитесь что dev сервер запущен** на `http://localhost:3000`
2. **Проверьте консоль** - тесты показывают где именно ошибка
3. **Посмотрите скриншоты** - они показывают состояние на момент теста
4. **Запустите в не-headless режиме** - уже настроено в `test-dashboard.js` (`headless: false`)

---

## Настройка

### Скорость выполнения

В `test-dashboard.js` можно изменить скорость:

```javascript
const browser = await chromium.launch({ 
  headless: false, 
  slowMo: 500  // Задержка в мс между действиями (500 = медленно, 0 = быстро)
});
```

### Headless режим

Для CI/CD можно включить headless режим:

```javascript
const browser = await chromium.launch({ headless: true });
```

---

## Интеграция с package.json

Можно добавить скрипты в `package.json`:

```json
{
  "scripts": {
    "test:e2e": "node tests/integration/test-dashboard.js",
    "test:theme": "node tests/integration/test-dashboard-quick.js"
  }
}
```

Тогда запуск будет проще:

```bash
npm run test:e2e
npm run test:theme
```

---

## Troubleshooting

### Ошибка: "Executable doesn't exist"

Установите браузеры Playwright:

```bash
npx playwright install
```

### Ошибка: "page.goto: net::ERR_CONNECTION_REFUSED"

Dev сервер Next.js не запущен. Запустите:

```bash
npm run dev
```

### Тесты проходят, но темная тема не работает

Запустите быструю проверку для диагностики:

```bash
node tests/integration/test-dashboard-quick.js
```

Посмотрите вывод - он покажет что именно не так с CSS переменными.

