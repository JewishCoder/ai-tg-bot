const { chromium } = require('playwright');

/**
 * Автоматизированное тестирование Dashboard
 * 
 * Запуск: node test-dashboard.js
 */

async function testDashboard() {
    console.log('🚀 Запуск автоматизированного тестирования Dashboard...\n');

    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    const context = await browser.newContext();
    const page = await context.newPage();

    let testsPassed = 0;
    let testsFailed = 0;

    const test = async (name, fn) => {
        try {
            await fn();
            console.log(`✅ ${name}`);
            testsPassed++;
        } catch (error) {
            console.log(`❌ ${name}`);
            console.log(`   Ошибка: ${error.message}\n`);
            testsFailed++;
        }
    };

    try {
        // Переход на dashboard
        await page.goto('http://localhost:3000/dashboard');
        await page.waitForLoadState('networkidle');

        console.log('📊 1. Тестирование светлой темы\n');

        // Проверка начального состояния
        await test('Страница загрузилась', async () => {
            await page.waitForSelector('h1:has-text("Dashboard")');
        });

        await test('Header отображается', async () => {
            await page.waitForSelector('header');
            const header = await page.locator('header').textContent();
            if (!header.includes('AI Telegram Bot Dashboard')) {
                throw new Error('Header не содержит заголовок');
            }
        });

        await test('3 Summary Cards отображаются', async () => {
            const cards = await page.locator('[role="main"] > div > div:nth-child(2) > div').count();
            if (cards < 3) {
                throw new Error(`Найдено ${cards} карточек вместо 3`);
            }
        });

        await test('График активности отображается', async () => {
            await page.waitForSelector('text=Активность по времени');
        });

        await test('Period Filter отображается', async () => {
            await page.waitForSelector('button:has-text("День")');
            await page.waitForSelector('button:has-text("Неделя")');
            await page.waitForSelector('button:has-text("Месяц")');
        });

        console.log('\n🔄 2. Тестирование интерактивности\n');

        // Тест Sidebar
        await test('Sidebar сворачивается/разворачивается', async () => {
            const trigger = page.getByRole('button', { name: 'Toggle Sidebar' });
            await trigger.click();
            await page.waitForTimeout(300);
            await trigger.click();
            await page.waitForTimeout(300);
        });

        // Тест Period Filter
        await test('Фильтр "День" работает', async () => {
            await page.getByRole('button', { name: 'День' }).click();
            await page.waitForTimeout(1000); // Ждем загрузки данных
            const dayButton = page.getByRole('button', { name: 'День' });
            const classes = await dayButton.getAttribute('class');
            if (!classes || !classes.includes('bg-')) {
                throw new Error('Кнопка "День" не активна');
            }
        });

        await test('Фильтр "Неделя" работает', async () => {
            await page.getByRole('button', { name: 'Неделя' }).click();
            await page.waitForTimeout(1000);
        });

        // Тест Collapsible Tables
        await test('Таблица "Последние диалоги" раскрывается', async () => {
            const button = page.locator('button').filter({ hasText: /^$/ }).first();
            await button.click();
            await page.waitForTimeout(500);
            const table = await page.locator('table').first().isVisible();
            if (!table) {
                throw new Error('Таблица не появилась');
            }
        });

        await test('Таблица "Топ пользователи" раскрывается', async () => {
            const button = page.locator('button').filter({ hasText: /^$/ }).nth(1);
            await button.click();
            await page.waitForTimeout(500);
            const tables = await page.locator('table').count();
            if (tables < 2) {
                throw new Error(`Найдено ${tables} таблиц вместо 2`);
            }
        });

        // Скриншот светлой темы
        await page.screenshot({ path: 'dashboard-light-auto.png', fullPage: true });
        console.log('📸 Скриншот светлой темы: dashboard-light-auto.png\n');

        console.log('🌙 3. Тестирование темной темы\n');

        // Переключение на темную тему
        await test('Переключение на темную тему', async () => {
            const themeToggle = page.getByRole('button', { name: 'Toggle theme' });
            await themeToggle.click();
            await page.waitForTimeout(500);

            // Проверяем что класс .dark добавлен к html
            const htmlClass = await page.locator('html').getAttribute('class');
            if (!htmlClass || !htmlClass.includes('dark')) {
                throw new Error('Класс .dark не добавлен к <html>');
            }
        });

        await test('Темный фон применился', async () => {
            const bodyBg = await page.evaluate(() => {
                return window.getComputedStyle(document.body).backgroundColor;
            });

            // Темный фон должен быть rgb(10, 10, 13) или близкий
            if (bodyBg.includes('255, 255, 255') || bodyBg.includes('rgb(255')) {
                throw new Error(`Фон все еще белый: ${bodyBg}`);
            }
            console.log(`   Background: ${bodyBg}`);
        });

        await test('Текст виден на темном фоне', async () => {
            const color = await page.evaluate(() => {
                return window.getComputedStyle(document.body).color;
            });

            // Светлый текст должен быть близок к белому
            if (color.includes('rgb(0') || color.includes('10, 10')) {
                throw new Error(`Текст темный на темном фоне: ${color}`);
            }
            console.log(`   Text color: ${color}`);
        });

        // Скриншот темной темы
        await page.screenshot({ path: 'dashboard-dark-auto.png', fullPage: true });
        console.log('📸 Скриншот темной темы: dashboard-dark-auto.png\n');

        console.log('🔙 4. Возврат к светлой теме\n');

        await test('Переключение на светлую тему', async () => {
            const themeToggle = page.getByRole('button', { name: 'Toggle theme' });
            await themeToggle.click();
            await page.waitForTimeout(500);

            const htmlClass = await page.locator('html').getAttribute('class');
            if (htmlClass && htmlClass.includes('dark')) {
                throw new Error('Класс .dark не удален из <html>');
            }
        });

    } catch (error) {
        console.error('\n❌ Критическая ошибка:', error.message);
        testsFailed++;
    } finally {
        await browser.close();
    }

    // Итоговый отчет
    console.log('\n' + '='.repeat(50));
    console.log('📊 ИТОГОВЫЙ ОТЧЕТ');
    console.log('='.repeat(50));
    console.log(`✅ Тестов пройдено: ${testsPassed}`);
    console.log(`❌ Тестов провалено: ${testsFailed}`);
    console.log(`📈 Процент успеха: ${Math.round((testsPassed / (testsPassed + testsFailed)) * 100)}%`);
    console.log('='.repeat(50) + '\n');

    if (testsFailed === 0) {
        console.log('🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!\n');
    } else {
        console.log('⚠️  Есть проваленные тесты. Проверьте вывод выше.\n');
    }

    process.exit(testsFailed > 0 ? 1 : 0);
}

testDashboard();

