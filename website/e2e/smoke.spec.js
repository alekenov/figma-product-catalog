/**
 * E2E Smoke Test: Basic page load
 *
 * Tests that the homepage loads and displays products
 */
import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('homepage loads and shows products', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check title
    await expect(page).toHaveTitle(/Cvety/);

    // Wait for products to load with extended timeout
    await page.waitForSelector('[data-testid="product-card"]', {
      timeout: 30000,
      state: 'visible'
    });

    // Verify at least one product is visible
    const products = await page.locator('[data-testid="product-card"]').count();
    expect(products).toBeGreaterThan(0);

    console.log(`✓ Found ${products} products on homepage`);
  });

  test('cart icon is visible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that cart icon exists
    const cartIcon = page.locator('[data-testid="cart-icon"]');
    await expect(cartIcon).toBeVisible();
  });
});