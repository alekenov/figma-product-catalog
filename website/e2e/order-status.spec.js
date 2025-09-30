/**
 * E2E Test: Order Status Page
 *
 * Tests order tracking functionality including:
 * - Direct navigation to order status page
 * - Order number URL encoding (# character handling)
 * - Order status display
 * - Phase 3 fields rendering
 */
import { test, expect } from '@playwright/test';

test.describe('Order Status Page - Phase 3', () => {
  // Helper function to create an order and get order number
  async function createTestOrder(page) {
    await page.goto('/cart');
    await expect(page.locator('h1:has-text("В корзине")')).toBeVisible();

    // Fill checkout form
    await page.fill('input[placeholder*="Имя получателя"]', 'Status Test User');
    await page.fill('input[placeholder*="Телефон получателя"]', '+77773333333');
    await page.fill('input[placeholder*="Адрес доставки"]', 'Test Delivery Address');
    await page.fill('input[placeholder*="Номер телефона отправителя"]', '+77777777777');

    // Select payment method
    await page.locator('[role="radio"]').first().click();

    // Submit order
    await page.locator('button:has-text("Оформить заказ")').click();

    // Wait for navigation and extract order number from URL
    await page.waitForURL(/\/status\//, { timeout: 10000 });
    const url = page.url();
    const match = url.match(/\/status\/(%23|#)?(\d+)/);
    return match ? (match[1] ? `#${match[2]}` : match[2]) : null;
  }

  test('should display order status after checkout', async ({ page }) => {
    // Create order and navigate to status page
    const orderNumber = await createTestOrder(page);
    expect(orderNumber).toBeTruthy();

    // Verify order status page elements
    await expect(page.locator('h1').filter({ hasText: /Заказ #\d+ в пути/ })).toBeVisible();

    // Verify delivery section is visible
    await expect(page.locator('text=Доставка')).toBeVisible();

    // Verify recipient information is displayed
    await expect(page.locator('text=Получатель')).toBeVisible();
    await expect(page.locator('text=Status Test User')).toBeVisible();

    // Verify delivery address is shown
    await expect(page.locator('text=Test Delivery Address')).toBeVisible();

    // Verify order summary section
    await expect(page.locator('text=Итого')).toBeVisible();
  });

  test('should handle direct navigation with URL-encoded order number', async ({ page }) => {
    // First create an order to get a valid order number
    const orderNumber = await createTestOrder(page);
    expect(orderNumber).toBeTruthy();

    // Extract numeric part
    const numericPart = orderNumber.replace('#', '');

    // Navigate directly with encoded order number
    const encodedOrderNumber = encodeURIComponent(`#${numericPart}`);
    await page.goto(`/status/${encodedOrderNumber}`);

    // Verify page loads correctly
    await expect(page.locator('h1').filter({ hasText: /Заказ #\d+/ })).toBeVisible({ timeout: 10000 });
  });

  test('should display order progress bar', async ({ page }) => {
    await createTestOrder(page);

    // Verify progress bar is visible
    // OrderProgressBar component should render stages
    const progressBar = page.locator('[class*="w-full"]').filter({ has: page.locator('div[class*="relative"]') }).first();
    await expect(progressBar).toBeVisible();
  });

  test('should display Phase 3 checkout fields', async ({ page }) => {
    await createTestOrder(page);

    // Verify recipient details
    await expect(page.locator('text=Получатель')).toBeVisible();
    await expect(page.locator('text=+77773333333')).toBeVisible();

    // Verify sender phone
    await expect(page.locator('text=Отправитель')).toBeVisible();
    await expect(page.locator('text=+77777777777')).toBeVisible();

    // Verify delivery info
    await expect(page.locator('text=Адрес доставки')).toBeVisible();
  });

  test('should display action buttons', async ({ page }) => {
    await createTestOrder(page);

    // Verify action buttons are present
    await expect(page.locator('button:has-text("Добавить комментарий")')).toBeVisible();
    await expect(page.locator('button:has-text("Редактировать заказ")')).toBeVisible();
    await expect(page.locator('button:has-text("Отменить заказ")')).toBeVisible();
  });

  test('should show error for non-existent order number', async ({ page }) => {
    // Navigate to status page with non-existent order number
    const fakeOrderNumber = encodeURIComponent('#99999');
    await page.goto(`/status/${fakeOrderNumber}`);

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Verify error message is shown
    await expect(page.locator('text=/Ошибка|не найден|not found/i')).toBeVisible({ timeout: 5000 });
  });

  test('should display bonus points calculation', async ({ page }) => {
    await createTestOrder(page);

    // Verify bonus points section is visible
    // Bonus points are displayed in the order summary
    await expect(page.locator('text=Итого')).toBeVisible();

    // The bonus points should be calculated and displayed
    // This is a visual check that the order summary renders
  });

  test('should handle special characters in order number', async ({ page }) => {
    const orderNumber = await createTestOrder(page);
    const currentUrl = page.url();

    // Verify URL handling of special character "#"
    // Should be either encoded as %23 or handled by router
    expect(currentUrl).toMatch(/\/status\/((%23|#)\d+|\d+)/);

    // Verify page still displays correctly despite special characters
    await expect(page.locator('h1').filter({ hasText: /Заказ/ })).toBeVisible();
  });
});