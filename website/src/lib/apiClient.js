/**
 * Type-Safe API Client
 *
 * Wraps the existing API service with Zod validation for runtime type safety.
 * All API calls validate responses against schemas before returning data.
 */
import * as api from '../services/api';
import * as schemas from './schemas';

/**
 * Generic validation wrapper
 * @param {Promise} apiCall - The API call promise
 * @param {z.ZodSchema} schema - The Zod schema to validate against
 * @returns {Promise} Validated data
 */
async function validateResponse(apiCall, schema) {
  try {
    const data = await apiCall;
    return schema.parse(data);
  } catch (error) {
    console.error('API response validation failed:', error);
    console.error('Error name:', error?.name);
    console.error('Error message:', error?.message);
    console.error('Error issues:', error?.issues);
    if (error.name === 'ZodError') {
      throw new Error(`Invalid API response: ${error.issues.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')}`);
    }
    throw error;
  }
}

// ========== Product APIs ==========

/**
 * Fetch home products with optional filters
 * @param {string|null} city - City filter
 * @param {Array<string>} tags - Tag filters
 * @returns {Promise<HomeProducts>}
 */
export async function fetchHomeProducts(city = null, tags = []) {
  return validateResponse(
    api.fetchHomeProducts(city, tags),
    schemas.HomeProductsSchema
  );
}

/**
 * Fetch available filters for products
 * @returns {Promise<Filters>}
 */
export async function fetchFilters() {
  return validateResponse(
    api.fetchFilters(),
    schemas.FiltersSchema
  );
}

/**
 * Fetch single product by ID
 * @param {number} productId - Product ID
 * @returns {Promise<Product>}
 */
export async function fetchProduct(productId) {
  return validateResponse(
    api.fetchProduct(productId),
    schemas.ProductSchema
  );
}

/**
 * Fetch complete product details with all relationships
 * @param {number} productId - Product ID
 * @returns {Promise<ProductDetail>}
 */
export async function fetchProductDetail(productId) {
  return validateResponse(
    api.fetchProductDetail(productId),
    schemas.ProductDetailSchema
  );
}

// ========== Order APIs ==========

/**
 * Preview order before checkout - validates inventory and calculates totals
 * @param {Array<{product_id: number, quantity: number}>} items - Cart items
 * @returns {Promise<OrderPreview>}
 */
export async function previewOrder(items) {
  return validateResponse(
    api.previewOrder(items),
    schemas.OrderPreviewSchema
  );
}

/**
 * Create order with items and full checkout data
 * @param {Object} orderData - Complete order data
 * @returns {Promise<Order>}
 */
export async function createOrder(orderData) {
  return validateResponse(
    api.createOrder(orderData),
    schemas.OrderSchema
  );
}

/**
 * Fetch order status by order number
 * @param {string} orderNumber - Order number (e.g., "#12345")
 * @returns {Promise<OrderStatus>}
 */
export async function fetchOrderStatus(orderNumber) {
  return validateResponse(
    api.fetchOrderStatus(orderNumber),
    schemas.OrderStatusSchema
  );
}

// ========== Review APIs ==========

/**
 * Fetch company reviews with statistics
 * @param {number} limit - Maximum number of reviews
 * @param {number} offset - Pagination offset
 * @returns {Promise<CompanyReviewsResponse>}
 */
export async function fetchCompanyReviews(limit = 10, offset = 0) {
  return validateResponse(
    api.fetchCompanyReviews(limit, offset),
    schemas.CompanyReviewsResponseSchema
  );
}

/**
 * Submit a company review
 * @param {Object} reviewData - Review data {author_name, rating, text}
 * @returns {Promise<ReviewItem>}
 */
export async function submitCompanyReview(reviewData) {
  return validateResponse(
    api.submitCompanyReview(reviewData),
    schemas.ReviewItemSchema
  );
}

// ========== FAQ APIs ==========

/**
 * Fetch FAQs with optional category filter
 * @param {string|null} category - Filter by category
 * @returns {Promise<Array<FAQ>>}
 */
export async function fetchFAQs(category = null) {
  return validateResponse(
    api.fetchFAQs(category),
    schemas.FAQsResponseSchema
  );
}