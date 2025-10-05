/**
 * API Service Layer
 *
 * Centralized API client for communicating with the backend.
 * All functions use the generic apiRequest utility for consistency.
 */

import { get, post } from './apiRequest';

/**
 * Fetch home products with optional filters
 *
 * @param {string|null} city - City filter (e.g., "almaty", "astana")
 * @param {Array<string>} tags - Array of tag filters (e.g., ["roses", "urgent"])
 * @returns {Promise<{featured: Array, available_tags: Array, bestsellers: Array}>}
 */
export async function fetchHomeProducts(city = null, tags = []) {
  const params = {};
  if (city) params.city = city;
  if (tags.length > 0) params.tags = tags;

  return get('/products/home', params, 'Failed to fetch home products');
}

/**
 * Fetch available filters for products
 *
 * @returns {Promise<{tags: Array, cities: Array, price_range: Object, product_types: Array}>}
 */
export async function fetchFilters() {
  return get('/products/filters', null, 'Failed to fetch filters');
}

/**
 * Fetch single product details by ID
 *
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} Product details
 */
export async function fetchProduct(productId) {
  return get(`/products/${productId}`, null, `Failed to fetch product ${productId}`);
}

/**
 * Fetch complete product details with all relationships
 *
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} Complete product details including images, variants,
 *                            composition, addons, bundles, reviews, and pickup locations
 */
export async function fetchProductDetail(productId) {
  return get(`/products/${productId}/detail`, null, `Failed to fetch product detail ${productId}`);
}

/**
 * Preview order before checkout - validates inventory and calculates totals
 *
 * @param {Array<{product_id: number, quantity: number}>} items - Cart items to preview
 * @returns {Promise<{available: boolean, items: Array, warnings: Array, estimated_total: number}>}
 */
export async function previewOrder(items) {
  return post('/orders/preview', items, 'Failed to preview order');
}

/**
 * Create order with items and full checkout data
 *
 * @param {Object} orderData - Complete order data including recipient, sender, delivery, payment
 * @returns {Promise<Object>} Created order with order_number
 */
export async function createOrder(orderData) {
  return post('/orders/with-items', orderData, 'Failed to create order');
}

/**
 * Fetch order status by order number (DEPRECATED)
 *
 * @param {string} orderNumber - Order number (e.g., "#12345" or already encoded "%2300001")
 * @returns {Promise<Object>} Order status details
 * @deprecated Use fetchOrderByTrackingId instead for better security
 */
export async function fetchOrderStatus(orderNumber) {
  // URL-encode the order number to handle special characters like "#"
  const encodedOrderNumber = encodeURIComponent(orderNumber);
  return get(
    `/orders/by-number/${encodedOrderNumber}/status`,
    null,
    `Failed to fetch order status for ${orderNumber}`
  );
}

/**
 * Fetch order status by tracking ID (secure 9-digit ID)
 *
 * @param {string} trackingId - 9-digit tracking ID (e.g., "847562910")
 * @returns {Promise<Object>} Order status details
 */
export async function fetchOrderByTrackingId(trackingId) {
  return get(
    `/orders/by-tracking/${trackingId}/status`,
    null,
    `Failed to fetch order by tracking ID ${trackingId}`
  );
}

/**
 * Submit feedback for order photo (like/dislike)
 *
 * @param {string} trackingId - Tracking ID (9-digit secure ID)
 * @param {string} feedback - "like" or "dislike"
 * @param {string|null} comment - Optional comment (especially for dislike)
 * @returns {Promise<Object>} Feedback submission result
 */
export async function submitPhotoFeedback(trackingId, feedback, comment = null) {
  return post(
    `/orders/by-tracking/${trackingId}/photo/feedback`,
    { feedback, comment },
    `Failed to submit photo feedback for tracking ID ${trackingId}`
  );
}

/**
 * Fetch company reviews with statistics
 *
 * @param {number} limit - Maximum number of reviews to return (default: 10)
 * @param {number} offset - Number of reviews to skip for pagination (default: 0)
 * @returns {Promise<{reviews: Array, stats: Object}>} Reviews and statistics
 */
export async function fetchCompanyReviews(limit = 10, offset = 0) {
  return get('/reviews/company', { limit, offset }, 'Failed to fetch company reviews');
}

/**
 * Submit a company review
 *
 * @param {Object} reviewData - Review data {author_name, rating, text}
 * @returns {Promise<Object>} Created review
 */
export async function submitCompanyReview(reviewData) {
  return post('/reviews/company', reviewData, 'Failed to submit company review');
}

/**
 * Fetch FAQs with optional category filter
 *
 * @param {string|null} category - Filter by category (e.g., "delivery", "orders")
 * @returns {Promise<Array>} Array of FAQ objects
 */
export async function fetchFAQs(category = null) {
  const params = category ? { category } : null;
  return get('/faqs', params, 'Failed to fetch FAQs');
}

/**
 * Fetch public shop settings
 *
 * @returns {Promise<Object>} Shop settings including hours, delivery costs, etc.
 */
export async function fetchPublicShopSettings() {
  return get('/shop/settings/public', null, 'Failed to fetch shop settings');
}
