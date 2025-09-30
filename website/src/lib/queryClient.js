/**
 * React Query Client Configuration
 *
 * Configures QueryClient with optimized defaults for the application.
 */
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: Data remains fresh for 5 minutes
      staleTime: 5 * 60 * 1000,

      // Cache time: Data remains in cache for 10 minutes
      gcTime: 10 * 60 * 1000,

      // Retry failed requests once
      retry: 1,

      // Retry delay: 1 second
      retryDelay: 1000,

      // Refetch on window focus for real-time updates
      refetchOnWindowFocus: true,

      // Don't refetch on mount if data is fresh
      refetchOnMount: false,

      // Don't refetch on reconnect if data is fresh
      refetchOnReconnect: false,
    },
    mutations: {
      // Retry mutations once
      retry: 1,

      // Retry delay: 1 second
      retryDelay: 1000,
    },
  },
});

/**
 * Query keys for consistent cache management
 */
export const queryKeys = {
  // Products
  homeProducts: (city, tags) => ['products', 'home', { city, tags }],
  product: (id) => ['products', id],
  productDetail: (id) => ['products', id, 'detail'],
  filters: () => ['products', 'filters'],

  // Orders
  orderPreview: (items) => ['orders', 'preview', items],
  orderStatus: (orderNumber) => ['orders', orderNumber, 'status'],

  // Reviews
  companyReviews: (limit, offset) => ['reviews', 'company', { limit, offset }],

  // FAQs
  faqs: (category) => ['faqs', { category }],
};