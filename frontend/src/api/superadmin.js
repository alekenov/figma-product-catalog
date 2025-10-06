/**
 * Superadmin API Module
 * Handles all API calls for superadmin functionality
 */
import { authenticatedFetch, API_BASE_URL } from '../services/api';

const BASE_URL = `${API_BASE_URL}/superadmin`;

/**
 * Helper function to make authenticated API requests
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @returns {Promise<any>} Response data
 */
const apiRequest = async (url, options = {}) => {
  const { method = 'GET', params, body } = options;

  // Build URL with query parameters
  let fullUrl = url;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      fullUrl = `${url}?${queryString}`;
    }
  }

  // Make authenticated request
  const response = await authenticatedFetch(fullUrl, {
    method,
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return await response.json();
};

/**
 * Shop Management API
 */
export const shopAPI = {
  /**
   * Get all shops
   * @param {Object} params - Query parameters
   * @param {boolean} params.is_active - Filter by active status
   * @param {number} params.skip - Skip N records
   * @param {number} params.limit - Limit results
   * @returns {Promise<Array>} Array of shops
   */
  list: async (params = {}) => {
    return apiRequest(`${BASE_URL}/shops`, {
      method: 'GET',
      params
    });
  },

  /**
   * Get shop details with users and statistics
   * @param {number} shopId - Shop ID
   * @returns {Promise<Object>} Shop details
   */
  getDetail: async (shopId) => {
    return apiRequest(`${BASE_URL}/shops/${shopId}`, {
      method: 'GET'
    });
  },

  /**
   * Block a shop
   * @param {number} shopId - Shop ID
   * @returns {Promise<Object>} Updated shop
   */
  block: async (shopId) => {
    return apiRequest(`${BASE_URL}/shops/${shopId}/block`, {
      method: 'PUT'
    });
  },

  /**
   * Unblock a shop
   * @param {number} shopId - Shop ID
   * @returns {Promise<Object>} Updated shop
   */
  unblock: async (shopId) => {
    return apiRequest(`${BASE_URL}/shops/${shopId}/unblock`, {
      method: 'PUT'
    });
  }
};

/**
 * User Management API
 */
export const userAPI = {
  /**
   * Get all users across all shops
   * @param {Object} params - Query parameters
   * @param {number} params.shop_id - Filter by shop ID
   * @param {string} params.role - Filter by role
   * @param {boolean} params.is_active - Filter by active status
   * @param {string} params.search - Search by name or phone
   * @param {number} params.skip - Skip N records
   * @param {number} params.limit - Limit results
   * @returns {Promise<Array>} Array of users
   */
  list: async (params = {}) => {
    return apiRequest(`${BASE_URL}/users`, {
      method: 'GET',
      params
    });
  },

  /**
   * Block a user
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Updated user
   */
  block: async (userId) => {
    return apiRequest(`${BASE_URL}/users/${userId}/block`, {
      method: 'PUT'
    });
  },

  /**
   * Unblock a user
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Updated user
   */
  unblock: async (userId) => {
    return apiRequest(`${BASE_URL}/users/${userId}/unblock`, {
      method: 'PUT'
    });
  },

  /**
   * Reset user password
   * @param {number} userId - User ID
   * @param {string} newPassword - New password
   * @returns {Promise<Object>} Success response
   */
  resetPassword: async (userId, newPassword) => {
    return apiRequest(`${BASE_URL}/users/${userId}/reset-password`, {
      method: 'POST',
      params: { new_password: newPassword }
    });
  }
};

/**
 * Statistics API
 */
export const statsAPI = {
  /**
   * Get platform-wide statistics
   * @returns {Promise<Object>} Platform statistics
   */
  getPlatformStats: async () => {
    return apiRequest(`${BASE_URL}/stats`, {
      method: 'GET'
    });
  }
};

export default {
  shop: shopAPI,
  user: userAPI,
  stats: statsAPI
};
