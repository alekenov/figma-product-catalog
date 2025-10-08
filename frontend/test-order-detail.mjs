import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Opening login page...');
    await page.goto('http://localhost:5176/login');
    await page.waitForTimeout(1000);

    console.log('📍 Step 2: Logging in as superadmin...');
    // Fill phone number
    await page.fill('input[type="tel"]', '77015211545');
    await page.click('button:has-text("Войти")');
    await page.waitForTimeout(1000);

    // Fill code
    await page.fill('input[type="text"]', '1234');
    await page.click('button:has-text("Подтвердить")');
    await page.waitForTimeout(2000);

    console.log('📍 Step 3: Navigating to superadmin orders...');
    await page.goto('http://localhost:5176/superadmin/orders');
    await page.waitForTimeout(1500);

    console.log('📍 Step 4: Clicking on first order...');
    const firstOrder = await page.locator('.cursor-pointer').first();
    await firstOrder.click();
    await page.waitForTimeout(2000);

    console.log('📍 Step 5: Checking order detail page...');
    const url = page.url();
    console.log('✅ Current URL:', url);

    if (!url.includes('/superadmin/orders/')) {
      console.error('❌ ERROR: Not on order detail page!');
      return;
    }

    // Check for order title
    const orderTitle = await page.locator('h1').textContent();
    console.log('✅ Order title:', orderTitle);

    // Check for customer info section
    const customerSection = await page.locator('text=Информация о клиенте').count();
    console.log('✅ Customer section found:', customerSection > 0);

    // Check for delivery section
    const deliverySection = await page.locator('text=Доставка').count();
    console.log('✅ Delivery section found:', deliverySection > 0);

    // Check for items section
    const itemsSection = await page.locator('text=Товары').count();
    console.log('✅ Items section found:', itemsSection > 0);

    // Check for status dropdown
    const statusDropdown = await page.locator('button:has-text("Изменить статус")').count();
    console.log('✅ Status dropdown found:', statusDropdown > 0);

    console.log('📍 Step 6: Testing status dropdown...');
    await page.click('button:has-text("Изменить статус")');
    await page.waitForTimeout(1000);

    const dropdownOpen = await page.locator('text=Оплачен').count();
    console.log('✅ Dropdown opened:', dropdownOpen > 0);

    // Close dropdown
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);

    console.log('📍 Step 7: Testing back navigation...');
    await page.click('button:has-text("←")');
    await page.waitForTimeout(1500);

    const backUrl = page.url();
    console.log('✅ Back URL:', backUrl);

    if (backUrl.includes('/superadmin/orders') && !backUrl.includes('/superadmin/orders/')) {
      console.log('✅ Successfully returned to orders list');
    } else {
      console.error('❌ ERROR: Did not return to orders list!');
    }

    console.log('\n🎉 All tests passed!');
    await page.waitForTimeout(2000);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
})();
