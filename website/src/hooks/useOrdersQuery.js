/**
 * React Query Hooks for Orders
 *
 * Handles order preview, creation, and status tracking with optimistic updates.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as apiClient from '../lib/apiClient';
import { queryKeys } from '../lib/queryClient';

/**
 * Preview order before checkout
 * @param {Array<{product_id: number, quantity: number}>} items - Cart items
 * @param {boolean} enabled - Whether to fetch (default: false, manual trigger)
 */
export function useOrderPreview(items, enabled = false) {
  return useQuery({
    queryKey: queryKeys.orderPreview(items),
    queryFn: () => apiClient.previewOrder(items),
    enabled: enabled && items.length > 0,
    // Don't cache preview results (always fresh)
    staleTime: 0,
    gcTime: 0,
  });
}

/**
 * Create order mutation
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderData) => apiClient.createOrder(orderData),
    onSuccess: (data) => {
      // Invalidate order status query for the new order
      queryClient.invalidateQueries({
        queryKey: queryKeys.orderStatus(data.orderNumber),
      });
    },
  });
}

/**
 * Fetch order status by order number
 * @param {string} orderNumber - Order number (e.g., "#12345")
 * @param {boolean} enabled - Whether to fetch (default: true)
 */
export function useOrderStatus(orderNumber, enabled = true) {
  return useQuery({
    queryKey: queryKeys.orderStatus(orderNumber),
    queryFn: () => apiClient.fetchOrderStatus(orderNumber),
    enabled: enabled && !!orderNumber,
    // Refetch every 30 seconds for real-time status updates
    refetchInterval: 30 * 1000,
  });
}