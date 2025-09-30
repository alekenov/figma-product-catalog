/**
 * React Query Hooks for Reviews
 *
 * Handles fetching and submitting company reviews with automatic cache updates.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as apiClient from '../lib/apiClient';
import { queryKeys } from '../lib/queryClient';

/**
 * Fetch company reviews with statistics
 * @param {number} limit - Maximum number of reviews (default: 10)
 * @param {number} offset - Pagination offset (default: 0)
 */
export function useCompanyReviews(limit = 10, offset = 0) {
  return useQuery({
    queryKey: queryKeys.companyReviews(limit, offset),
    queryFn: () => apiClient.fetchCompanyReviews(limit, offset),
  });
}

/**
 * Submit company review mutation
 */
export function useSubmitCompanyReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reviewData) => apiClient.submitCompanyReview(reviewData),
    onSuccess: () => {
      // Invalidate all company reviews queries to refetch with new review
      queryClient.invalidateQueries({
        queryKey: ['reviews', 'company'],
      });
    },
  });
}