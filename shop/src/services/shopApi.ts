/**
 * Shop API service
 * Handles fetching shop information and products from backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

export interface ShopInfo {
  id: number;
  name: string;
  phone: string | null;
  address: string | null;
  city: string | null;
  weekday_start: string;
  weekday_end: string;
  weekday_closed: boolean;
  weekend_start: string;
  weekend_end: string;
  weekend_closed: boolean;
  delivery_cost_tenge: number;
  free_delivery_amount_tenge: number;
  pickup_available: boolean;
  delivery_available: boolean;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  type: string;
  description: string | null;
  enabled: boolean;
  is_featured: boolean;
  image: string | null;
  images: ProductImage[];
  colors: string[] | null;
  occasions: string[] | null;
  cities: string[] | null;
  tags: string[] | null;
  manufacturingTime: number | null;
}

export interface ProductImage {
  id: number;
  url: string;
  order: number;
  is_primary: boolean;
}

/**
 * Fetch shop information (public endpoint, no auth required)
 */
export async function fetchShopInfo(shopId: number): Promise<ShopInfo> {
  const response = await fetch(`${API_BASE_URL}/shop/settings/public?shop_id=${shopId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch shop info: ${response.statusText}`);
  }

  const data = await response.json();

  // Transform to match ShopInfo interface
  return {
    id: shopId,
    name: data.shop_name,
    phone: data.phone,
    address: data.address,
    city: data.city,
    weekday_start: data.weekday_hours?.split(' - ')[0] || '09:00',
    weekday_end: data.weekday_hours?.split(' - ')[1] || '18:00',
    weekday_closed: data.weekday_closed || false,
    weekend_start: data.weekend_hours?.split(' - ')[0] || '10:00',
    weekend_end: data.weekend_hours?.split(' - ')[1] || '17:00',
    weekend_closed: data.weekend_closed || false,
    delivery_cost_tenge: data.delivery_cost_tenge,
    free_delivery_amount_tenge: data.free_delivery_threshold_tenge,
    pickup_available: data.pickup_available,
    delivery_available: data.delivery_available,
  };
}

/**
 * Fetch products for a specific shop (public endpoint, no auth required)
 */
export async function fetchShopProducts(
  shopId: number,
  options: {
    limit?: number;
    skip?: number;
    enabledOnly?: boolean;
    search?: string;
    minPrice?: number;
    maxPrice?: number;
    type?: string;
  } = {}
): Promise<Product[]> {
  const {
    limit = 100,
    skip = 0,
    enabledOnly = true,
    search,
    minPrice,
    maxPrice,
    type,
  } = options;

  const params = new URLSearchParams({
    shop_id: shopId.toString(),
    limit: limit.toString(),
    skip: skip.toString(),
    enabled_only: enabledOnly.toString(),
  });

  if (search) params.set('search', search);
  if (minPrice) params.set('min_price', minPrice.toString());
  if (maxPrice) params.set('max_price', maxPrice.toString());
  if (type) params.set('type', type);

  const response = await fetch(`${API_BASE_URL}/products?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch products: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch featured products for a shop
 */
export async function fetchFeaturedProducts(shopId: number, limit: number = 20): Promise<Product[]> {
  const allProducts = await fetchShopProducts(shopId, { limit, enabledOnly: true });
  return allProducts.filter(p => p.is_featured);
}

/**
 * Fetch single product by ID
 */
export async function fetchProduct(productId: number): Promise<Product> {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch product: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check if shop is currently open based on working hours
 */
export function isShopOpen(shop: ShopInfo): boolean {
  const now = new Date();
  const currentDay = now.getDay(); // 0 = Sunday, 6 = Saturday
  const isWeekend = currentDay === 0 || currentDay === 6;
  const currentTime = now.toTimeString().slice(0, 5); // HH:MM format

  if (isWeekend) {
    if (shop.weekend_closed) return false;
    return currentTime >= shop.weekend_start && currentTime <= shop.weekend_end;
  } else {
    if (shop.weekday_closed) return false;
    return currentTime >= shop.weekday_start && currentTime <= shop.weekday_end;
  }
}

/**
 * Format working hours for display
 */
export function formatWorkingHours(shop: ShopInfo): string {
  const weekdayHours = shop.weekday_closed
    ? 'Закрыто'
    : `${shop.weekday_start} - ${shop.weekday_end}`;
  const weekendHours = shop.weekend_closed
    ? 'Закрыто'
    : `${shop.weekend_start} - ${shop.weekend_end}`;

  return `Пн-Пт: ${weekdayHours}, Сб-Вс: ${weekendHours}`;
}
