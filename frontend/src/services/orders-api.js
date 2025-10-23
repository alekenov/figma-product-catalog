/**
 * Orders API module
 * Handles order CRUD operations, status updates, tracking, and photos
 */

import { API_BASE_URL, authenticatedFetch, handleApiError } from './api-client.js';

export const ordersAPI = {
  /**
   * Get all orders with optional filtering
   * @param {Object} params Query parameters
   * @returns {Promise<Object>} Orders data with pagination
   */
  getOrders: async (params = {}) => {
    const searchParams = new URLSearchParams();

    if (params.skip) searchParams.append('skip', params.skip);
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.status) searchParams.append('status', params.status);
    if (params.customer_phone) searchParams.append('customer_phone', params.customer_phone);
    if (params.search) searchParams.append('search', params.search);

    const url = `${API_BASE_URL}/orders/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await authenticatedFetch(url);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Get single order by ID
   * @param {string|number} orderId Order ID
   * @returns {Promise<Object>} Order data
   */
  getOrder: async (orderId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}`);

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new order
   * @param {Object} orderData Order data
   * @returns {Promise<Object>} Created order
   */
  createOrder: async (orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/`, {
      method: 'POST',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Create new order with items
   * @param {Object} orderData Order data with items
   * @returns {Promise<Object>} Created order
   */
  createOrderWithItems: async (orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/with-items`, {
      method: 'POST',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update order
   * @param {string|number} orderId Order ID
   * @param {Object} orderData Order data
   * @returns {Promise<Object>} Updated order
   */
  updateOrder: async (orderId, orderData) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: 'PUT',
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Update order status
   * @param {string|number} orderId Order ID
   * @param {string} status New order status
   * @param {string|null} notes Optional notes
   * @returns {Promise<Object>} Updated order
   */
  updateOrderStatus: async (orderId, status, notes = null) => {
    const params = new URLSearchParams({ status });
    if (notes) params.append('notes', notes);

    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/status?${params.toString()}`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Add item to order
   * @param {string|number} orderId Order ID
   * @param {string|number} productId Product ID
   * @param {number} quantity Item quantity
   * @param {string|null} specialRequests Optional special requests
   * @returns {Promise<Object>} Updated order
   */
  addOrderItem: async (orderId, productId, quantity, specialRequests = null) => {
    const params = new URLSearchParams({
      product_id: productId,
      quantity: quantity
    });
    if (specialRequests) params.append('special_requests', specialRequests);

    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/items?${params.toString()}`, {
      method: 'POST',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Upload photo for order (before delivery)
   * @param {string|number} orderId Order ID
   * @param {File} file Image file
   * @returns {Promise<Object>} Upload result with photo URL
   */
  uploadOrderPhoto: async (orderId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    // For FormData, we need to let the browser set Content-Type with boundary
    // So we use fetch directly instead of authenticatedFetch
    const token = getToken();
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/photo`, {
      method: 'POST',
      body: formData,
      headers: headers
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  },

  /**
   * Delete photo from order
   * @param {string|number} orderId Order ID
   * @returns {Promise<Object>} Delete result
   */
  deleteOrderPhoto: async (orderId) => {
    const response = await authenticatedFetch(`${API_BASE_URL}/orders/${orderId}/photo`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    return await response.json();
  }
};

// Products API
