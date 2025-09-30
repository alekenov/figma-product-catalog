/**
 * React Query Hooks for Products
 *
 * Type-safe hooks using React Query for automatic caching,
 * loading states, and error handling.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as apiClient from '../lib/apiClient';
import { queryKeys } from '../lib/queryClient';

/**
 * Fetch home products with optional filters
 * @param {string|null} city - City filter
 * @param {Array<string>} tags - Tag filters
 */
export function useHomeProducts(city = null, tags = []) {
  return useQuery({
    queryKey: queryKeys.homeProducts(city, tags),
    queryFn: () => apiClient.fetchHomeProducts(city, tags),
    select: (data) => ({
      products: data.featured || [],
      availableTags: data.available_tags || [],
      bestsellers: data.bestsellers || [],
    }),
  });
}

/**
 * Fetch available product filters
 */
export function useFilters() {
  return useQuery({
    queryKey: queryKeys.filters(),
    queryFn: () => apiClient.fetchFilters(),
  });
}

/**
 * Fetch single product by ID
 * @param {number} productId - Product ID
 * @param {boolean} enabled - Whether to fetch (default: true)
 */
export function useProduct(productId, enabled = true) {
  return useQuery({
    queryKey: queryKeys.product(productId),
    queryFn: () => apiClient.fetchProduct(productId),
    enabled: enabled && !!productId,
  });
}

/**
 * Fetch complete product details with all relationships
 * @param {number} productId - Product ID
 * @param {boolean} enabled - Whether to fetch (default: true)
 */
export function useProductDetail(productId, enabled = true) {
  return useQuery({
    queryKey: queryKeys.productDetail(productId),
    queryFn: () => apiClient.fetchProductDetail(productId),
    enabled: enabled && !!productId,
  });
}