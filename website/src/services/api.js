/**
 * API Service Layer
 *
 * Centralized API client for communicating with the backend.
 * Base URL is configured via environment variable VITE_API_BASE_URL.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

/**
 * Fetch home products with optional filters
 *
 * @param {string|null} city - City filter (e.g., "almaty", "astana")
 * @param {Array<string>} tags - Array of tag filters (e.g., ["roses", "urgent"])
 * @returns {Promise<{featured: Array, available_tags: Array, bestsellers: Array}>}
 */
export async function fetchHomeProducts(city = null, tags = []) {
  const params = new URLSearchParams();

  if (city) {
    params.append('city', city);
  }

  if (tags.length > 0) {
    params.append('tags', tags.join(','));
  }

  const url = `${API_BASE_URL}/products/home${params.toString() ? '?' + params.toString() : ''}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch home products:', error);
    throw error;
  }
}

/**
 * Fetch available filters for products
 *
 * @returns {Promise<{tags: Array, cities: Array, price_range: Object, product_types: Array}>}
 */
export async function fetchFilters() {
  const url = `${API_BASE_URL}/products/filters`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch filters:', error);
    throw error;
  }
}

/**
 * Fetch single product details by ID
 *
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} Product details
 */
export async function fetchProduct(productId) {
  const url = `${API_BASE_URL}/products/${productId}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Product not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch product ${productId}:`, error);
    throw error;
  }
}

/**
 * Fetch complete product details with all relationships
 *
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} Complete product details including images, variants,
 *                            composition, addons, bundles, reviews, and pickup locations
 */
export async function fetchProductDetail(productId) {
  const url = `${API_BASE_URL}/products/${productId}/detail`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Product not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch product detail ${productId}:`, error);
    throw error;
  }
}