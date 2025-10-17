const { chromium } = require('playwright');

/**
 * Быстрая проверка темной темы
 * 
 * Запуск: node test-dashboard-quick.js
 */

async function quickTest() {
    console.log('⚡ Быстрая проверка темной темы...\n');

    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await page.goto('http://localhost:3000/dashboard');
        await page.waitForTimeout(2000);

        console.log('📊 Светлая тема:');
        let bodyBg = await page.evaluate(() => window.getComputedStyle(document.body).backgroundColor);
        let bodyColor = await page.evaluate(() => window.getComputedStyle(document.body).color);
        let htmlClass = await page.locator('html').getAttribute('class');

        console.log(`  HTML class: "${htmlClass || 'none'}"`);
        console.log(`  Background: ${bodyBg}`);
        console.log(`  Text color: ${bodyColor}\n`);

        console.log('🔄 Переключаю на темную тему...');
        await page.getByRole('button', { name: 'Toggle theme' }).click();
        await page.waitForTimeout(1000);

        console.log('\n🌙 Темная тема:');
        bodyBg = await page.evaluate(() => window.getComputedStyle(document.body).backgroundColor);
        bodyColor = await page.evaluate(() => window.getComputedStyle(document.body).color);
        htmlClass = await page.locator('html').getAttribute('class');

        console.log(`  HTML class: "${htmlClass || 'none'}"`);
        console.log(`  Background: ${bodyBg}`);
        console.log(`  Text color: ${bodyColor}`);

        // Проверка результата
        const isDark = htmlClass && htmlClass.includes('dark');
        const hasDarkBg = !bodyBg.includes('255, 255, 255');

        console.log('\n' + '='.repeat(50));
        if (isDark && hasDarkBg) {
            console.log('✅ ТЕМНАЯ ТЕМА РАБОТАЕТ КОРРЕКТНО!');
        } else {
            console.log('❌ ТЕМНАЯ ТЕМА НЕ РАБОТАЕТ:');
            if (!isDark) console.log('   - Класс .dark не добавлен к <html>');
            if (!hasDarkBg) console.log('   - Фон остался белым');
        }
        console.log('='.repeat(50) + '\n');

        await page.screenshot({ path: 'dark-theme-check.png', fullPage: true });
        console.log('📸 Скриншот сохранен: dark-theme-check.png\n');

    } catch (error) {
        console.error('❌ Ошибка:', error.message);
    } finally {
        await browser.close();
    }
}

quickTest();

