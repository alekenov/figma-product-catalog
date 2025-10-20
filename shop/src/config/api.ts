/**
 * API Configuration
 *
 * Centralized configuration for all API calls.
 * Single source of truth for API endpoints and settings.
 *
 * Usage:
 *   import { API_CONFIG } from '../config/api';
 *   fetch(`${API_CONFIG.BASE_URL}/products`)
 */

/**
 * API base URL - loaded from environment variable
 * Falls back to localhost for local development
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

/**
 * Default shop ID for single-shop deployments
 * Can be overridden via environment variable
 */
export const DEFAULT_SHOP_ID = parseInt(import.meta.env.VITE_SHOP_ID || '8', 10);

/**
 * Request timeout in milliseconds
 */
export const REQUEST_TIMEOUT = 30000; // 30 seconds

/**
 * API configuration object
 * Export as object for easier mocking in tests
 */
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  SHOP_ID: DEFAULT_SHOP_ID,
  TIMEOUT: REQUEST_TIMEOUT,
} as const;

/**
 * Helper to build full API URL from endpoint path
 *
 * @param endpoint - API endpoint path (e.g., "/products")
 * @returns Full URL (e.g., "http://localhost:8014/api/v1/products")
 *
 * @example
 * const url = buildApiUrl('/products');
 * // Returns: "http://localhost:8014/api/v1/products"
 */
export function buildApiUrl(endpoint: string): string {
  // Ensure endpoint starts with /
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${path}`;
}

export default API_CONFIG;
