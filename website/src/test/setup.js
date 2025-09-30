/**
 * Vitest Setup File
 *
 * Configures testing environment before running tests.
 */
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test case (unmount React components)
afterEach(() => {
  cleanup();
});