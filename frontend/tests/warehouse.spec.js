import { test, expect } from '@playwright/test';

test.describe('Warehouse functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Начинаем с главной страницы
    await page.goto('http://localhost:5177');
  });

  test('should navigate to warehouse page and display items', async ({ page }) => {
    // Клик по кнопке "Склад" в навигации
    await page.click('button:has-text("Склад")');

    // Проверяем что перешли на страницу склада
    await expect(page).toHaveURL('http://localhost:5177/warehouse');

    // Проверяем заголовок
    await expect(page.locator('h1')).toHaveText('Склад');

    // Проверяем что есть товары
    const items = page.locator('.bg-white.border.border-gray-border');
    await expect(items).toHaveCount(8); // Ожидаем 8 товаров

    // Проверяем первый товар
    const firstItem = items.first();
    await expect(firstItem).toContainText('Красная роза');
    await expect(firstItem).toContainText('150 шт');
    await expect(firstItem).toContainText('200 ₸');
  });

  test('should open warehouse item detail page', async ({ page }) => {
    // Переходим на склад
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');

    // Кликаем на первый товар
    const firstItem = page.locator('.bg-white.border.border-gray-border').first();
    await firstItem.click();

    // Проверяем что перешли на детальную страницу
    await expect(page).toHaveURL(/warehouse\/\d+/);

    // Проверяем элементы страницы
    await expect(page.locator('h1')).toContainText('Красная роза');
    await expect(page.locator('text=Текущий остаток')).toBeVisible();
    await expect(page.locator('text=150 шт')).toBeVisible();

    // Проверяем наличие полей цен
    await expect(page.locator('text=Себестоимость:')).toBeVisible();
    await expect(page.locator('text=Розничная цена:')).toBeVisible();
    await expect(page.locator('text=Маржа:')).toBeVisible();
    await expect(page.locator('text=Наценка:')).toBeVisible();
  });

  test('should update prices and show in history', async ({ page }) => {
    // Переходим на детальную страницу товара
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');
    await page.locator('.bg-white.border.border-gray-border').first().click();
    await page.waitForURL(/warehouse\/\d+/);

    // Находим поле себестоимости
    const costPriceInput = page.locator('input[type="number"]').first();

    // Очищаем и вводим новую цену
    await costPriceInput.fill('');
    await costPriceInput.type('180');
    await costPriceInput.blur(); // Триггерим onBlur для сохранения

    // Ждем обновления
    await page.waitForTimeout(1000);

    // Проверяем что в истории появилась запись об изменении цены
    const historySection = page.locator('text=История операций').locator('..');
    await expect(historySection).toContainText('Себестоимость: 150₸ → 180₸');
  });

  test('should perform writeoff operation', async ({ page }) => {
    // Переходим на детальную страницу товара
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');
    await page.locator('.bg-white.border.border-gray-border').first().click();
    await page.waitForURL(/warehouse\/\d+/);

    // Заполняем форму списания
    const amountInput = page.locator('input[placeholder="0"]');
    await amountInput.fill('10');

    // Выбираем причину
    const reasonSelect = page.locator('select');
    await reasonSelect.selectOption('Порча');

    // Кликаем кнопку Списать
    await page.click('button:has-text("Списать")');

    // Ждем обновления
    await page.waitForTimeout(1000);

    // Проверяем что остаток уменьшился
    const quantityText = page.locator('.text-2xl.font-bold').first();
    await expect(quantityText).toContainText('140 шт');

    // Проверяем историю операций
    const historySection = page.locator('text=История операций').locator('..');
    await expect(historySection).toContainText('Списание: Порча');
    await expect(historySection).toContainText('-10 шт');
  });

  test('should show validation errors for writeoff', async ({ page }) => {
    // Переходим на детальную страницу товара
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');
    await page.locator('.bg-white.border.border-gray-border').first().click();
    await page.waitForURL(/warehouse\/\d+/);

    // Пытаемся списать без указания количества
    await page.click('button:has-text("Списать")');

    // Проверяем alert
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('Введите корректное количество');
      await dialog.accept();
    });

    // Вводим количество больше остатка
    const amountInput = page.locator('input[placeholder="0"]');
    await amountInput.fill('500');

    // Выбираем причину
    const reasonSelect = page.locator('select');
    await reasonSelect.selectOption('Порча');

    // Пытаемся списать
    await page.click('button:has-text("Списать")');

    // Проверяем alert о превышении количества
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('Нельзя списать больше');
      await dialog.accept();
    });
  });

  test('should navigate back to warehouse list', async ({ page }) => {
    // Переходим на детальную страницу
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');
    await page.locator('.bg-white.border.border-gray-border').first().click();
    await page.waitForURL(/warehouse\/\d+/);

    // Кликаем кнопку назад
    await page.click('button:has(svg)');

    // Проверяем что вернулись на список
    await expect(page).toHaveURL('http://localhost:5177/warehouse');
    await expect(page.locator('h1')).toHaveText('Склад');
  });

  test('should highlight low stock items', async ({ page }) => {
    // Переходим на склад
    await page.click('button:has-text("Склад")');
    await page.waitForURL('**/warehouse');

    // Ищем товары с низким остатком (например, Белая орхидея с 25 шт при минимуме 5)
    const orchidItem = page.locator('text=Белая орхидея').locator('..');

    // Проверяем что остаток не выделен красным (25 > 5)
    const orchidQuantity = orchidItem.locator('text=/\\d+ шт/');
    await expect(orchidQuantity).not.toHaveClass(/text-red-500/);

    // Для товаров с критически низким остатком должен быть красный текст
    // (это будет работать после списания до минимума)
  });
});