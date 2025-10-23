/**
 * Authentication API module
 * Handles user authentication, token management, and password operations
 */

import {
  API_BASE_URL,
  authenticatedFetch,
  handleApiError,
  getToken,
  setToken,
  removeToken,
  getStoredUser,
  setStoredUser
} from './api-client.js';

/**
 * Authentication API
 */
export const authAPI = {
  /**
   * Login user with phone and password
   * @param {string} phone Phone number in Kazakhstan format
   * @param {string} password User password
   * @returns {Promise<Object>} Login response with token and user data
   */
  login: async (phone, password) => {
    console.log('🌐 [API] Login request starting...');
    console.log('   URL:', `${API_BASE_URL}/auth/login`);
    console.log('   Phone:', phone);
    console.log('   Password length:', password.length);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    });

    console.log('📡 [API] Response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      console.error('❌ [API] Login failed with status:', response.status);
      await handleApiError(response);
    }

    const data = await response.json();
    console.log('✅ [API] Login successful, user:', data.user?.name);

    // Store token and user data
    setToken(data.access_token);
    setStoredUser(data.user);
    console.log('💾 [API] Token and user stored in localStorage');

    return data;
  },

  /**
   * Refresh JWT token for current user
   * @returns {Promise<Object>} New token and user data
   */
  refresh: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const data = await response.json();

    // Update stored token and user data
    setToken(data.access_token);
    setStoredUser(data.user);

    return data;
  },

  /**
   * Logout current user
   * @returns {Promise<Object>} Logout response
   */
  logout: async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
      });

      const data = response.ok ? await response.json() : null;
      return data;
    } finally {
      // Always clear local storage regardless of API response
      removeToken();
    }
  },

  /**
   * Get current user information
   * @returns {Promise<Object>} Current user data
   */
  me: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/me`);

    if (!response.ok) {
      await handleApiError(response);
    }

    const user = await response.json();
    setStoredUser(user);
    return user;
  },

  /**
   * Register new user
   * @param {Object} userData User registration data
   * @returns {Promise<Object>} Created user data
   */
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Change user password
   * @param {string} currentPassword Current password
   * @param {string} newPassword New password
   * @returns {Promise<Object>} Success response
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Verify if current token is valid
   * @returns {Promise<Object>} Token verification result
   */
  verifyToken: async () => {
    const response = await authenticatedFetch(`${API_BASE_URL}/auth/verify-token`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} True if user has valid token
   */
  isAuthenticated: () => {
    const token = getToken();
    const user = getStoredUser();
    return !!(token && user);
  }
};
