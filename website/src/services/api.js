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

/**
 * Preview order before checkout - validates inventory and calculates totals
 *
 * @param {Array<{product_id: number, quantity: number}>} items - Cart items to preview
 * @returns {Promise<{available: boolean, items: Array, warnings: Array, estimated_total: number}>}
 */
export async function previewOrder(items) {
  const url = `${API_BASE_URL}/orders/preview`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(items),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to preview order:', error);
    throw error;
  }
}

/**
 * Create order with items and full checkout data
 *
 * @param {Object} orderData - Complete order data including recipient, sender, delivery, payment
 * @returns {Promise<Object>} Created order with order_number
 */
export async function createOrder(orderData) {
  const url = `${API_BASE_URL}/orders/with-items`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create order:', error);
    throw error;
  }
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
  // If already encoded (from useParams), encodeURIComponent is safe to call again
  const encodedOrderNumber = encodeURIComponent(orderNumber);
  const url = `${API_BASE_URL}/orders/by-number/${encodedOrderNumber}/status`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Order not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch order status for ${orderNumber}:`, error);
    throw error;
  }
}

/**
 * Fetch order status by tracking ID (secure 9-digit ID)
 *
 * @param {string} trackingId - 9-digit tracking ID (e.g., "847562910")
 * @returns {Promise<Object>} Order status details
 */
export async function fetchOrderByTrackingId(trackingId) {
  const url = `${API_BASE_URL}/orders/by-tracking/${trackingId}/status`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Order not found');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch order by tracking ID ${trackingId}:`, error);
    throw error;
  }
}

/**
 * Fetch company reviews with statistics
 *
 * @param {number} limit - Maximum number of reviews to return (default: 10)
 * @param {number} offset - Number of reviews to skip for pagination (default: 0)
 * @returns {Promise<{reviews: Array, stats: Object}>} Reviews and statistics
 */
export async function fetchCompanyReviews(limit = 10, offset = 0) {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  const url = `${API_BASE_URL}/reviews/company?${params.toString()}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch company reviews:', error);
    throw error;
  }
}

/**
 * Submit a company review
 *
 * @param {Object} reviewData - Review data {author_name, rating, text}
 * @returns {Promise<Object>} Created review
 */
export async function submitCompanyReview(reviewData) {
  const url = `${API_BASE_URL}/reviews/company`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reviewData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to submit company review:', error);
    throw error;
  }
}

/**
 * Fetch FAQs with optional category filter
 *
 * @param {string|null} category - Filter by category (e.g., "delivery", "orders")
 * @returns {Promise<Array>} Array of FAQ objects
 */
export async function fetchFAQs(category = null) {
  const params = new URLSearchParams();

  if (category) {
    params.append('category', category);
  }

  const url = `${API_BASE_URL}/faqs${params.toString() ? '?' + params.toString() : ''}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch FAQs:', error);
    throw error;
  }
}

/**
 * Fetch public shop settings
 *
 * @returns {Promise<Object>} Shop settings including hours, delivery costs, etc.
 */
export async function fetchPublicShopSettings() {
  const url = `${API_BASE_URL}/shop/settings/public`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch shop settings:', error);
    throw error;
  }
}