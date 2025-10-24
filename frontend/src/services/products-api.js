/**
 * Products API module
 * Handles product catalog operations, images, and filtering
 */

import { API_BASE_URL, authenticatedFetch, handleApiError } from './api-client.js';

export const productsAPI = {
  /**
   * Get all products with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Object>} Products data with pagination
   */
  getProducts: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.type) searchParams.append('type', params.type);
    if (params.enabled_only !== undefined) searchParams.append('enabled_only', params.enabled_only);
    if (params.search) searchParams.append('search', params.search);
    if (params.min_price) searchParams.append('min_price', params.min_price);
    if (params.max_price) searchParams.append('max_price', params.max_price);

    const url = `${API_BASE_URL}/products/admin${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: [...]}
    // or local API format [...]
    if (json && json.success && Array.isArray(json.data)) {
      return json.data;
    }

    return json;
  },

  /**
   * Get single product by ID
   * @param {string|number} productId Product ID
   * @returns {Promise<Object>} Product data
   */
  getProduct: async (productId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: {...}}
    // or local API format {...}
    if (json && json.success && json.data) {
      return json.data;
    }

    return json;
  },

  /**
   * Create new product
   * @param {Object} productData Product data
   * @returns {Promise<Object>} Created product
   */
  createProduct: async (productData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: {...}}
    // or local API format {...}
    if (json && json.success && json.data) {
      return json.data;
    }

    return json;
  },

  /**
   * Update product
   * @param {string|number} productId Product ID
   * @param {Object} productData Product data
   * @returns {Promise<Object>} Updated product
   */
  updateProduct: async (productId, productData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: {...}}
    // or local API format {...}
    if (json && json.success && json.data) {
      return json.data;
    }

    return json;
  },

  /**
   * Toggle product status
   * @param {string|number} productId Product ID
   * @param {boolean} enabled Enable/disable status
   * @returns {Promise<Object>} Updated product
   */
  toggleProductStatus: async (productId, enabled) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}/status?enabled=${enabled}`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: {...}}
    // or local API format {...}
    if (json && json.success && json.data) {
      return json.data;
    }

    return json;
  },

  /**
   * Delete product
   * @param {string|number} productId Product ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  deleteProduct: async (productId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const json = await response.json();

    // Handle production API format {success: true, data: {...}}
    // or local API format {...}
    if (json && json.success && json.data) {
      return json.data;
    }

    return json;
  }
};

// Clients API
