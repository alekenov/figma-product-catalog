/**
 * Products API for Bitrix v2
 * Handles product operations: list, get, create, update
 */

import { bitrixFetch, buildQueryString } from './bitrix-client.js';
import { adaptProduct, serializeProductForBitrix } from './bitrix-adapters.js';

export const productsAPI = {
  /**
   * Get list of products with optional filtering
   * @param {Object} params - Query parameters
   * @param {number} params.skip - Pagination offset
   * @param {number} params.limit - Pagination limit
   * @param {string} params.type - Filter by type
   * @param {string} params.search - Search query
   * @returns {Promise<Object>} Products with pagination
   */
  getProducts: async (params = {}) => {
    try {
      const queryParams = {};

      if (params.skip) queryParams.offset = params.skip;
      if (params.limit) queryParams.limit = params.limit;
      if (params.type) queryParams.type = params.type;
      if (params.search) queryParams.search = params.search;
      if (params.enabled_only !== undefined) {
        queryParams.isAvailable = params.enabled_only;
      } else {
        queryParams.isAvailable = false;
      }

      const query = buildQueryString(queryParams);
      const response = await bitrixFetch(`/products/${query}`);
      const rawProducts = Array.isArray(response.data) ? response.data : [];

      return {
        products: rawProducts.map(adaptProduct),
        pagination: {
          total: response.pagination?.total || rawProducts.length,
          has_more: response.pagination?.hasMore || false,
          limit: params.limit || 20,
          offset: params.skip || 0,
        }
      };
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  /**
   * Get single product by ID
   * @param {number|string} productId - Product ID
   * @returns {Promise<Object>} Product data
   */
  getProduct: async (productId, options = {}) => {
    try {
      // Try list endpoint first (has price as formatted string, works better)
      const listQuery = buildQueryString({
        id: productId,
        limit: 1
      });
      const listResponse = await bitrixFetch(`/products/${listQuery}`);

      if (listResponse.data && Array.isArray(listResponse.data) && listResponse.data.length > 0) {
        return adaptProduct(listResponse.data[0]);
      }

      // Fallback: detail endpoint with query format
      const detailQuery = buildQueryString({ id: productId });
      const detailResponse = await bitrixFetch(`/products/detail/${detailQuery}`);
      const productData = detailResponse.data || detailResponse;
      return adaptProduct(productData);
    } catch (error) {
      console.error(`Error fetching product ${productId}:`, error);
      throw error;
    }
  },

  /**
   * Create new product
   * @param {Object} productData - Product data in internal format
   * @returns {Promise<Object>} Created product
   */
  createProduct: async (productData) => {
    try {
      // Convert to Bitrix format
      const bitrixData = serializeProductForBitrix(productData);

      const response = await bitrixFetch('/products/', {
        method: 'POST',
        body: JSON.stringify(bitrixData)
      });

      const createdProduct = response.data || response;
      return adaptProduct(createdProduct);
    } catch (error) {
      console.error('Error creating product:', error);
      throw error;
    }
  },

  /**
   * Update existing product
   * @param {number|string} productId - Product ID
   * @param {Object} productData - Updated product data
   * @returns {Promise<Object>} Updated product
   */
  updateProduct: async (productId, productData) => {
    try {
      const bitrixData = serializeProductForBitrix(productData);

      const response = await bitrixFetch(`/products/${productId}/`, {
        method: 'PUT',
        body: JSON.stringify(bitrixData)
      });

      const updatedProduct = response.data || response;
      return adaptProduct(updatedProduct);
    } catch (error) {
      console.error(`Error updating product ${productId}:`, error);
      throw error;
    }
  },

  /**
   * Toggle product status (enabled/disabled)
   * @param {number|string} productId - Product ID
   * @param {boolean} enabled - Desired status
   * @returns {Promise<Object>} Updated product
   */
  toggleProductStatus: async (productId, enabled) => {
    try {
      const response = await bitrixFetch(`/products/${productId}/status?enabled=${enabled}`, {
        method: 'PATCH'
      });

      const productData = response.data || response;
      return adaptProduct(productData);
    } catch (error) {
      console.error(`Error toggling product ${productId} status:`, error);
      throw error;
    }
  },

  /**
   * Delete product
   * @param {number|string} productId - Product ID
   * @returns {Promise<Object>} Deletion response
   */
  deleteProduct: async (productId) => {
    try {
      const response = await bitrixFetch(`/products/${productId}/`, {
        method: 'DELETE'
      });

      return response;
    } catch (error) {
      console.error(`Error deleting product ${productId}:`, error);
      throw error;
    }
  },
};

export default productsAPI;
