/**
 * Orders API for Bitrix v2
 * Handles order operations: list, get, update status
 */

import { bitrixFetch, buildQueryString } from './bitrix-client.js';
import { adaptOrder } from './bitrix-adapters.js';

export const ordersAPI = {
  /**
   * Get list of orders with optional filtering
   * @param {Object} params - Query parameters
   * @param {number} params.skip - Pagination offset (maps to offset in v2)
   * @param {number} params.limit - Pagination limit
   * @param {string} params.status - Filter by status
   * @returns {Promise<Object>} Orders with pagination
   */
  getOrders: async (params = {}) => {
    try {
      const queryParams = {};

      if (params.skip) queryParams.offset = params.skip;
      if (params.limit) queryParams.limit = params.limit;
      if (params.status) queryParams.status = params.status;

      const query = buildQueryString(queryParams);
      const response = await bitrixFetch(`/orders/${query}`);

      return {
        orders: response.data.map(adaptOrder),
        pagination: {
          total: response.pagination?.total || response.data.length,
          has_more: response.pagination?.hasMore || false,
          limit: params.limit || 20,
          offset: params.skip || 0,
        }
      };
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  },

  /**
   * Get single order by ID
   * @param {number|string} orderId - Order ID
   * @returns {Promise<Object>} Order data
   */
  getOrder: async (orderId) => {
    try {
      const response = await bitrixFetch(`/orders/detail/?id=${orderId}`);

      // Response might return order data directly or in data wrapper
      const orderData = response.data || response;
      const adapted = adaptOrder(orderData);

      // Import formatOrderForDisplay dynamically to avoid circular dependency
      const { formatOrderForDisplay } = await import('./formatters.js');
      return formatOrderForDisplay(adapted);
    } catch (error) {
      console.error(`Error fetching order ${orderId}:`, error);
      throw error;
    }
  },

  /**
   * Update order status
   * @param {number|string} orderId - Order ID
   * @param {string} status - New status
   * @returns {Promise<Object>} Updated order
   */
  updateOrderStatus: async (orderId, status) => {
    try {
      const response = await bitrixFetch(`/orders/${orderId}/status/`, {
        method: 'PATCH',
        body: JSON.stringify({ status })
      });

      const orderData = response.data || response;
      const adapted = adaptOrder(orderData);

      // Apply formatting
      const { formatOrderForDisplay } = await import('./formatters.js');
      return formatOrderForDisplay(adapted);
    } catch (error) {
      console.error(`Error updating order ${orderId} status:`, error);
      throw error;
    }
  },

  /**
   * Create new order
   * @param {Object} orderData - Order data
   * @returns {Promise<Object>} Created order
   */
  createOrder: async (orderData) => {
    try {
      const response = await bitrixFetch('/orders/', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });

      const createdOrder = response.data || response;
      return adaptOrder(createdOrder);
    } catch (error) {
      console.error('Error creating order:', error);
      throw error;
    }
  },

  /**
   * Get user information by ID (for fetching florist, courier, manager names)
   * @param {number|string} userId - User ID
   * @returns {Promise<Object>} User data (id, name, email, phone)
   */
  getUserInfo: async (userId) => {
    try {
      const response = await bitrixFetch(`/users/${userId}/`);
      const userData = response.data || response;

      return {
        id: userData.id,
        name: userData.name || userData.userName || 'Unknown',
        email: userData.email || '',
        phone: userData.phone || '',
      };
    } catch (error) {
      console.warn(`Could not fetch user ${userId}:`, error);
      // Return placeholder user instead of throwing
      return {
        id: userId,
        name: 'Unknown',
        email: '',
        phone: '',
      };
    }
  },
};

export default ordersAPI;
