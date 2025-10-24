/**
 * Bitrix API Client
 * HTTP client for cvety.kz/api/v2/ with Bearer token authentication
 */

// Use environment variable for API URL (Railway), or fallback to proxy (dev/Cloudflare)
const BITRIX_API_URL = import.meta.env.VITE_BITRIX_API_URL || '/api/v2';
const BITRIX_TOKEN = import.meta.env.VITE_BITRIX_TOKEN;
const BITRIX_CITY = import.meta.env.VITE_BITRIX_CITY || 'astana'; // Default to Astana

if (!BITRIX_TOKEN) {
  console.warn('VITE_BITRIX_TOKEN not set in environment variables');
}

/**
 * Generic Bitrix API fetch wrapper
 * @param {string} endpoint - API endpoint (e.g., '/products/')
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} API response with { success, data, pagination }
 */
export async function bitrixFetch(endpoint, options = {}) {
  const url = `${BITRIX_API_URL}${endpoint}`;

  // Only add Content-Type for POST/PUT/PATCH requests
  // Bitrix API breaks on GET requests with Content-Type header
  const method = options.method || 'GET';
  const needsContentType = ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase());

  const headers = {
    'Authorization': `Bearer ${BITRIX_TOKEN}`,
    'X-City': BITRIX_CITY,
    ...options.headers
  };

  if (needsContentType) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Some endpoints may return empty body (e.g. 204)
    const text = await response.text();
    const data = text ? JSON.parse(text) : null;

    // Legacy Bitrix responses include { success, data }
    if (data && Object.prototype.hasOwnProperty.call(data, 'success')) {
      if (!data.success) {
        throw new Error(data.error || 'Bitrix API returned success: false');
      }
      return data;
    }

    // New FastAPI endpoints return raw JSON (object/array/message)
    return {
      success: true,
      data,
      // Preserve pagination if backend adds it at top level
      pagination: data && data.pagination ? data.pagination : undefined,
    };
  } catch (error) {
    console.error(`Bitrix API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Build query string from params object
 * @param {Object} params - Query parameters
 * @returns {string} - URL encoded query string
 */
export function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value);
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}
