/**
 * React Query Hook for FAQs
 *
 * Handles fetching frequently asked questions with optional category filter.
 */
import { useQuery } from '@tanstack/react-query';
import * as apiClient from '../lib/apiClient';
import { queryKeys } from '../lib/queryClient';

/**
 * Fetch FAQs with optional category filter
 * @param {string|null} category - Filter by category (default: null for all)
 */
export function useFAQs(category = null) {
  return useQuery({
    queryKey: queryKeys.faqs(category),
    queryFn: () => apiClient.fetchFAQs(category),
  });
}