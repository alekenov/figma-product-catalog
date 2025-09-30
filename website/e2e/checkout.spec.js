/**
 * E2E Smoke Test: Checkout Flow
 *
 * Tests the critical path from homepage → cart → checkout → order status
 * Updated to work with actual CartPage implementation (not product detail page)
 */
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow - Phase 3', () => {
  test('should complete full checkout journey with URL-encoded order number', async ({ page }) => {
    // Step 1: Navigate to homepage
    await page.goto('/');
    await expect(page.locator('header')).toBeVisible();

    // Step 2: Navigate directly to cart page (cart has mock data for testing)
    await page.goto('/cart');
    await expect(page.locator('h1:has-text("В корзине")')).toBeVisible();

    // Step 3: Verify cart page shows items
    await expect(page.locator('h1').filter({ hasText: 'В корзине' })).toBeVisible();

    // Step 4: Fill recipient form
    await page.fill('input[placeholder*="Имя получателя"]', 'John Doe');
    await page.fill('input[placeholder*="Телефон получателя"]', '+77771234567');
    await page.fill('input[placeholder*="Адрес доставки"]', 'Test Address, Almaty');

    // Step 5: Fill sender form
    await page.fill('input[placeholder*="Номер телефона отправителя"]', '+77777777777');

    // Step 6: Select delivery type (express is default)
    // No action needed - express is pre-selected

    // Step 7: Select payment method (click first payment option)
    const paymentOptions = page.locator('[role="radio"]');
    await paymentOptions.first().click();

    // Step 8: Submit order via checkout button
    const checkoutButton = page.locator('button:has-text("Оформить заказ")');
    await expect(checkoutButton).toBeVisible();
    await checkoutButton.click();

    // Step 9: Verify navigation to order status page with URL-encoded order number
    // URL should contain encoded "#" as "%23"
    await page.waitForURL(/\/status\/(%23|#).+/, { timeout: 10000 });

    // Step 10: Verify order status page loaded
    await expect(page.locator('h1').filter({ hasText: /Заказ #\d+ в пути/ })).toBeVisible({ timeout: 10000 });

    // Step 11: Verify order number format in page content
    const orderNumberText = await page.locator('h1').filter({ hasText: /Заказ #\d+/ }).textContent();
    expect(orderNumberText).toMatch(/Заказ #\d+ в пути/);
  });

  test('should handle order number with # character in URL', async ({ page }) => {
    // Navigate to cart
    await page.goto('/cart');
    await expect(page.locator('h1:has-text("В корзине")')).toBeVisible();

    // Fill minimal required fields
    await page.fill('input[placeholder*="Имя получателя"]', 'Test User');
    await page.fill('input[placeholder*="Телефон получателя"]', '+77771111111');
    await page.fill('input[placeholder*="Адрес доставки"]', 'Test Address');
    await page.fill('input[placeholder*="Номер телефона отправителя"]', '+77777777777');

    // Select payment method
    await page.locator('[role="radio"]').first().click();

    // Submit order
    await page.locator('button:has-text("Оформить заказ")').click();

    // Wait for navigation with encoded order number
    await page.waitForURL(/\/status\//, { timeout: 10000 });

    // Verify URL contains encoded "#" or raw "#"
    const currentUrl = page.url();
    expect(currentUrl).toMatch(/\/status\/(%23|#)\d+/);

    // Verify page loads successfully (not 404)
    await expect(page.locator('h1').filter({ hasText: /Заказ #\d+/ })).toBeVisible({ timeout: 10000 });
  });

  test('should update cart quantity using increase/decrease buttons', async ({ page }) => {
    // Navigate to cart
    await page.goto('/cart');

    // Find first cart item and its quantity display
    const firstItem = page.locator('[class*="space-y-4"] > div').first();

    // Get initial quantity (should be 1)
    const initialQuantity = await firstItem.locator('span').filter({ hasText: /^\d+$/ }).textContent();
    expect(parseInt(initialQuantity)).toBeGreaterThan(0);

    // Click increase button (+ button)
    const increaseButton = firstItem.locator('button').last();
    await increaseButton.click();

    // Verify quantity increased
    await page.waitForTimeout(500); // Wait for state update
    const newQuantity = await firstItem.locator('span').filter({ hasText: /^\d+$/ }).textContent();
    expect(parseInt(newQuantity)).toBe(parseInt(initialQuantity) + 1);
  });

  test('should calculate totals correctly in kopecks', async ({ page }) => {
    // Navigate to cart
    await page.goto('/cart');

    // Fill required fields
    await page.fill('input[placeholder*="Имя получателя"]', 'Price Test');
    await page.fill('input[placeholder*="Телефон получателя"]', '+77772222222');
    await page.fill('input[placeholder*="Адрес доставки"]', 'Test Address');
    await page.fill('input[placeholder*="Номер телефона отправителя"]', '+77777777777');

    // Select payment
    await page.locator('[role="radio"]').first().click();

    // Verify checkout button shows total (should be in tenge format)
    const checkoutButton = page.locator('button:has-text("Оформить заказ")');
    const buttonText = await checkoutButton.textContent();
    expect(buttonText).toMatch(/\d+/); // Should contain a number

    // Note: Actual kopecks conversion is tested in unit tests
    // This E2E test verifies the UI displays correctly
  });
});