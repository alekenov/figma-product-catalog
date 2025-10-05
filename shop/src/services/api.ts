/**
 * Marketplace Public API Service
 *
 * Centralized API client for all marketplace endpoints.
 * All endpoints are public and don't require authentication.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

// ============================================================================
// Type Definitions (matching backend API responses)
// ============================================================================

export interface Shop {
  id: number;
  name: string;
  city?: string;
  phone?: string;
  address?: string;
  delivery_cost_tenge: number;
  delivery_available: boolean;
  pickup_available: boolean;
  rating?: number;
  review_count?: number;
  is_open?: boolean;
}

export interface ShopDetail extends Shop {
  weekday_start?: string;
  weekday_end?: string;
  weekday_closed?: boolean;
  weekend_start?: string;
  weekend_end?: string;
  weekend_closed?: boolean;
  free_delivery_amount_tenge?: number;
}

export interface Product {
  id: number;
  name: string;
  price: number; // in kopecks
  type: string;
  description?: string;
  manufacturingTime?: number;
  shelfLife?: number;
  enabled: boolean;
  is_featured: boolean;
  colors?: string[];
  occasions?: string[];
  cities?: string[];
  tags?: string[];
  image?: string;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  author_name: string;
  rating: number;
  text: string;
  likes: number;
  dislikes: number;
  shop_name?: string;
  created_at: string;
}

export interface ReviewStats {
  total_count: number;
  average_rating: number;
  rating_breakdown: {
    5: number;
    4: number;
    3: number;
    2: number;
    1: number;
  };
}

export interface ReviewsResponse {
  reviews: Review[];
  stats: ReviewStats;
  pagination: {
    limit: number;
    offset: number;
    has_more: boolean;
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Convert kopecks to tenge and format with thousands separator
 */
export function formatPrice(kopecks: number): string {
  const tenge = kopecks / 100;
  return `${tenge.toLocaleString('ru-KZ')} ₸`;
}

/**
 * Generic API fetch helper with error handling
 */
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// ============================================================================
// Shops API
// ============================================================================

export interface ListShopsParams {
  city?: string;
  skip?: number;
  limit?: number;
}

/**
 * Get list of active shops with delivery settings and ratings
 */
export async function getShops(params: ListShopsParams = {}): Promise<Shop[]> {
  const queryParams = new URLSearchParams();

  if (params.city) queryParams.append('city', params.city);
  if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());

  const query = queryParams.toString();
  return apiFetch<Shop[]>(`/shops${query ? `?${query}` : ''}`);
}

/**
 * Get detailed information about a specific shop
 */
export async function getShopDetail(shopId: number): Promise<ShopDetail> {
  return apiFetch<ShopDetail>(`/shops/${shopId}`);
}

/**
 * Get products for a specific shop
 */
export async function getShopProducts(
  shopId: number,
  params: { enabled?: boolean; skip?: number; limit?: number } = {}
): Promise<Product[]> {
  const queryParams = new URLSearchParams();

  if (params.enabled !== undefined) queryParams.append('enabled', params.enabled.toString());
  if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());

  const query = queryParams.toString();
  return apiFetch<Product[]>(`/shops/${shopId}/products${query ? `?${query}` : ''}`);
}

// ============================================================================
// Products API
// ============================================================================

/**
 * Get featured products across all shops for marketplace homepage
 */
export async function getFeaturedProducts(
  params: { skip?: number; limit?: number } = {}
): Promise<Product[]> {
  const queryParams = new URLSearchParams();

  if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());

  const query = queryParams.toString();
  return apiFetch<Product[]>(`/products/public/featured${query ? `?${query}` : ''}`);
}

/**
 * Get bestselling products sorted by order count
 */
export async function getBestsellers(limit: number = 20): Promise<Product[]> {
  return apiFetch<Product[]>(`/products/public/bestsellers?limit=${limit}`);
}

// ============================================================================
// Reviews API
// ============================================================================

/**
 * Get platform-wide reviews from all active shops
 */
export async function getPlatformReviews(
  params: { limit?: number; offset?: number } = {}
): Promise<ReviewsResponse> {
  const queryParams = new URLSearchParams();

  if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
  if (params.offset !== undefined) queryParams.append('offset', params.offset.toString());

  const query = queryParams.toString();
  return apiFetch<ReviewsResponse>(`/reviews/platform${query ? `?${query}` : ''}`);
}

// ============================================================================
// Export All
// ============================================================================

export const marketplaceApi = {
  shops: {
    list: getShops,
    detail: getShopDetail,
    products: getShopProducts,
  },
  products: {
    featured: getFeaturedProducts,
    bestsellers: getBestsellers,
  },
  reviews: {
    platform: getPlatformReviews,
  },
};

export default marketplaceApi;
