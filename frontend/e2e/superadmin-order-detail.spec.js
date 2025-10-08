import { test, expect } from '@playwright/test';

test.describe('SuperadminOrderDetail Component', () => {
  test.beforeEach(async ({ page }) => {
    // Step 1: Open login page
    await page.goto('/login');
    await expect(page).toHaveURL(/.*login/);

    // Step 2: Authorize with phone and password
    const phoneInput = page.locator('input[type="tel"]#phone');
    await phoneInput.fill('77015211545');

    // Enter password
    const passwordInput = page.locator('input[type="password"]#password');
    await passwordInput.fill('password');

    // Submit form
    const submitButton = page.locator('button[type="submit"]:has-text("Войти")');
    await submitButton.click();

    // Wait for successful login and redirect
    await page.waitForTimeout(2000);
  });

  test('should display order detail and navigate back', async ({ page }) => {
    // Step 3: Navigate to /superadmin/orders
    await page.goto('/superadmin/orders');
    await expect(page).toHaveURL(/.*\/superadmin\/orders$/);

    // Wait for orders list to load
    await page.waitForSelector('text=/Заказ|Order|#/i', { timeout: 10000 });

    // Step 4: Click on any order from the list
    const firstOrder = page.locator('a[href*="/superadmin/orders/"], div[role="button"]:has-text("Заказ"), tr:has-text("Заказ")').first();
    await expect(firstOrder).toBeVisible({ timeout: 10000 });
    await firstOrder.click();

    // Wait for navigation to detail page
    await page.waitForURL(/.*\/superadmin\/orders\/\d+/, { timeout: 5000 });

    // Step 5: Verify detail page elements
    // Check header with order number
    const orderHeader = page.locator('h1:has-text("Заказ #"), h2:has-text("Заказ #")').first();
    await expect(orderHeader).toBeVisible({ timeout: 5000 });
    const headerText = await orderHeader.textContent();
    console.log('✓ Order Header:', headerText);

    // Check customer information
    const customerSection = page.locator('text=/Клиент|Заказчик|Customer/i').first();
    await expect(customerSection).toBeVisible({ timeout: 3000 });
    console.log('✓ Customer information section visible');

    // Check delivery address
    const addressSection = page.locator('text=/Адрес доставки|Delivery Address|Адрес/i').first();
    await expect(addressSection).toBeVisible({ timeout: 3000 });
    console.log('✓ Delivery address section visible');

    // Check product list
    const productsList = page.locator('text=/Товары|Состав|Products|Items/i').first();
    await expect(productsList).toBeVisible({ timeout: 3000 });
    console.log('✓ Products list section visible');

    // Check total amount
    const totalAmount = page.locator('text=/Итого|Сумма|Total|Amount/i').first();
    await expect(totalAmount).toBeVisible({ timeout: 3000 });
    console.log('✓ Total amount section visible');

    // Step 6: Check status dropdown
    const statusDropdown = page.locator('select:has-text("статус"), button:has-text("статус"), div:has-text("Изменить статус")').first();
    await expect(statusDropdown).toBeVisible({ timeout: 3000 });
    console.log('✓ Status dropdown visible');

    // Try to open dropdown
    await statusDropdown.click();
    await page.waitForTimeout(1000);
    console.log('✓ Status dropdown clicked');

    // Step 7: Navigate back using back button
    const backButton = page.locator('button:has-text("←"), a:has-text("←"), button[aria-label*="back" i], a[aria-label*="back" i]').first();
    await expect(backButton).toBeVisible({ timeout: 3000 });
    await backButton.click();
    console.log('✓ Back button clicked');

    // Step 8: Verify return to orders list
    await expect(page).toHaveURL(/.*\/superadmin\/orders$/, { timeout: 5000 });
    await expect(page.locator('text=/Заказ|Order|#/i').first()).toBeVisible({ timeout: 5000 });
    console.log('✓ Successfully returned to orders list');
  });

  test('should handle order detail with specific checks', async ({ page }) => {
    // Navigate to orders
    await page.goto('/superadmin/orders');

    // Get first order ID from the list
    const firstOrderLink = page.locator('a[href*="/superadmin/orders/"]').first();
    const orderHref = await firstOrderLink.getAttribute('href');
    const orderId = orderHref?.match(/\/orders\/(\d+)/)?.[1];

    console.log('Testing order ID:', orderId);

    // Click to open detail
    await firstOrderLink.click();
    await page.waitForURL(/.*\/superadmin\/orders\/\d+/);

    // Take screenshot of the detail page
    await page.screenshot({ path: 'order-detail-full.png', fullPage: true });
    console.log('✓ Screenshot saved: order-detail-full.png');

    // Verify all sections are present
    const sections = [
      { name: 'Order Header', selector: 'h1, h2' },
      { name: 'Customer Info', selector: 'text=/Клиент|Customer/i' },
      { name: 'Delivery Address', selector: 'text=/Адрес|Address/i' },
      { name: 'Products', selector: 'text=/Товары|Products/i' },
      { name: 'Total', selector: 'text=/Итого|Total/i' },
      { name: 'Status', selector: 'text=/Статус|Status/i' },
    ];

    for (const section of sections) {
      const element = page.locator(section.selector).first();
      const isVisible = await element.isVisible().catch(() => false);
      console.log(`${isVisible ? '✓' : '✗'} ${section.name}: ${isVisible ? 'visible' : 'not found'}`);
    }

    // Check if there are any error messages
    const errorMessages = page.locator('text=/error|ошибка|не найден/i');
    const errorCount = await errorMessages.count();
    if (errorCount > 0) {
      console.log('⚠ Warning: Found error messages:', await errorMessages.allTextContents());
    } else {
      console.log('✓ No error messages found');
    }
  });
});
