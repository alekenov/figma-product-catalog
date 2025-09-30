import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 *
 * Runs end-to-end tests against local dev server or production.
 */
export default defineConfig({
  testDir: './e2e',

  // Maximum time one test can run
  timeout: 60 * 1000,

  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: 'html',

  // Shared settings for all tests
  use: {
    // Base URL for tests (can be overridden by TEST_URL env var)
    baseURL: process.env.TEST_URL || 'http://localhost:5177',

    // Collect trace on first retry
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'retain-on-failure',
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Use existing dev server (must be running separately)
  // Run: npm run dev (in separate terminal)
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:5177',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000,
  // },
});