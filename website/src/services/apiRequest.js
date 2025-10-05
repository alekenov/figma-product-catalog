/**
 * Generic API Request Utility
 *
 * Provides a centralized way to make HTTP requests with consistent error handling.
 * This reduces code duplication across all API functions.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

/**
 * Make a generic API request
 *
 * @param {string} endpoint - API endpoint (e.g., '/products/home')
 * @param {Object} options - Request options
 * @param {string} options.method - HTTP method (GET, POST, PUT, DELETE)
 * @param {Object} options.body - Request body (for POST/PUT)
 * @param {Object} options.params - URL query parameters
 * @param {Object} options.headers - Additional headers
 * @param {string} options.errorMessage - Custom error message prefix
 * @returns {Promise<any>} Response JSON
 */
export async function apiRequest(endpoint, options = {}) {
  const {
    method = 'GET',
    body = null,
    params = null,
    headers = {},
    errorMessage = 'API request failed'
  } = options;

  // Build URL with query parameters
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        if (Array.isArray(value)) {
          searchParams.append(key, value.join(','));
        } else {
          searchParams.append(key, value);
        }
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Build request options
  const requestOptions = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  };

  if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    requestOptions.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, requestOptions);

    // Handle non-OK responses
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Resource not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`${errorMessage}:`, error);
    throw error;
  }
}

/**
 * Convenience function for GET requests
 */
export async function get(endpoint, params = null, errorMessage = 'Failed to fetch data') {
  return apiRequest(endpoint, { params, errorMessage });
}

/**
 * Convenience function for POST requests
 */
export async function post(endpoint, body, errorMessage = 'Failed to create resource') {
  return apiRequest(endpoint, { method: 'POST', body, errorMessage });
}

/**
 * Convenience function for PUT requests
 */
export async function put(endpoint, body, errorMessage = 'Failed to update resource') {
  return apiRequest(endpoint, { method: 'PUT', body, errorMessage });
}

/**
 * Convenience function for DELETE requests
 */
export async function del(endpoint, errorMessage = 'Failed to delete resource') {
  return apiRequest(endpoint, { method: 'DELETE', errorMessage });
}
