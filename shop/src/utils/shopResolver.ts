/**
 * Shop resolver utility
 * Supports both subdomain (vetka.cvety.kz) and subfolder (cvety.kz/vetka) approaches
 */

export interface ShopConfig {
  id: number;
  slug: string;
  subdomain: string;
  name: string;
  description?: string;
}

/**
 * Shop configuration registry
 * Add new shops here as they are onboarded
 */
const SHOPS: ShopConfig[] = [
  {
    id: 8,
    slug: 'vetka',
    subdomain: 'vetka',
    name: 'Ветка',
    description: 'Доставка цветов в Алматы и Астане'
  },
  // Add more shops here as they register
  // { id: 9, slug: 'rosa', subdomain: 'rosa', name: 'Роза' },
];

/**
 * Get shop configuration from URL
 * Supports both subdomain and subfolder modes
 *
 * @returns ShopConfig or null if shop not found
 *
 * @example
 * // Subdomain mode: vetka.cvety.kz
 * getShopFromUrl() // { id: 8, slug: 'vetka', ... }
 *
 * @example
 * // Subfolder mode: cvety.kz/vetka
 * getShopFromUrl() // { id: 8, slug: 'vetka', ... }
 *
 * @example
 * // Local development: localhost:5180/vetka
 * getShopFromUrl() // { id: 8, slug: 'vetka', ... }
 */
export function getShopFromUrl(): ShopConfig | null {
  const hostname = window.location.hostname;
  const pathname = window.location.pathname;

  // Mode 1: Subdomain detection (vetka.cvety.kz)
  // Check if hostname has subdomain before main domain
  if (hostname.includes('.cvety.kz') && !hostname.startsWith('www.')) {
    const subdomain = hostname.split('.')[0];
    const shop = SHOPS.find(s => s.subdomain === subdomain);

    if (shop) {
      console.log('[ShopResolver] Detected shop from subdomain:', subdomain, shop);
      return shop;
    }
  }

  // Mode 2: Subfolder detection (cvety.kz/vetka or localhost:5180/vetka)
  // Extract first path segment
  const pathSegments = pathname.split('/').filter(Boolean);
  if (pathSegments.length > 0) {
    const slug = pathSegments[0];
    const shop = SHOPS.find(s => s.slug === slug);

    if (shop) {
      console.log('[ShopResolver] Detected shop from slug:', slug, shop);
      return shop;
    }
  }

  // Mode 3: Default to first shop for root path (for backwards compatibility)
  if (pathname === '/' && SHOPS.length > 0) {
    console.log('[ShopResolver] Using default shop:', SHOPS[0]);
    return SHOPS[0];
  }

  console.warn('[ShopResolver] No shop found in URL:', { hostname, pathname });
  return null;
}

/**
 * Get shop by ID
 */
export function getShopById(id: number): ShopConfig | null {
  return SHOPS.find(s => s.id === id) || null;
}

/**
 * Get shop by slug
 */
export function getShopBySlug(slug: string): ShopConfig | null {
  return SHOPS.find(s => s.slug === slug) || null;
}

/**
 * Get all available shops
 */
export function getAllShops(): ShopConfig[] {
  return SHOPS;
}

/**
 * Generate shop URL based on current environment
 * Returns subdomain URL in production, subfolder URL in development
 */
export function getShopUrl(shop: ShopConfig): string {
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const port = window.location.port;

  // Production: use subdomain if on cvety.kz
  if (hostname.includes('cvety.kz')) {
    return `${protocol}//${shop.subdomain}.cvety.kz`;
  }

  // Development: use subfolder
  const portSuffix = port ? `:${port}` : '';
  return `${protocol}//${hostname}${portSuffix}/${shop.slug}`;
}
