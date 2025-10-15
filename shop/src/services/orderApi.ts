/**
 * Order API service
 * Handles fetching and updating order information from backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

export interface OrderStatusResponse {
  tracking_id: string;
  order_number: string;
  status: 'confirmed' | 'preparing' | 'delivering' | 'delivered' | 'cancelled';
  recipient: {
    name: string;
    phone: string;
  };
  pickup_address: string;
  delivery_address: string;
  date_time: string;
  sender: {
    phone: string;
  };
  photos: Array<{
    url: string;
    label: string;
    feedback?: string;
    comment?: string;
  }>;
  items: Array<{
    name: string;
    price: number; // in kopecks
  }>;
  delivery_cost: number; // in kopecks
  delivery_type: string;
  total: number; // in kopecks
  bonus_points: number;
  // Kaspi Pay integration
  payment_method?: string;
  kaspi_payment_id?: string;
  kaspi_payment_status?: 'Wait' | 'Processed' | 'Error';
  kaspi_payment_created_at?: string;
}

export interface OrderUpdateData {
  delivery_address?: string;
  delivery_date?: string;
  delivery_time?: string;
  delivery_notes?: string;
  recipient_name?: string;
  notes?: string;
}

/**
 * Fetch order status by tracking ID (public endpoint, no auth required)
 */
export async function fetchOrderByTrackingId(trackingId: string): Promise<OrderStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/orders/by-tracking/${trackingId}/status`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Заказ не найден. Проверьте код отслеживания.');
    }
    throw new Error(`Failed to fetch order: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Update order details by tracking ID (customer-facing update)
 */
export async function updateOrderByTrackingId(
  trackingId: string,
  updates: OrderUpdateData
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/orders/by-tracking/${trackingId}?changed_by=customer`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update order');
  }
}

/**
 * Submit photo feedback (like/dislike)
 */
export async function submitPhotoFeedback(
  trackingId: string,
  feedback: 'like' | 'dislike',
  comment?: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/orders/by-tracking/${trackingId}/photo/feedback`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ feedback, comment }),
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit feedback');
  }
}

/**
 * Helper to format order status for display
 */
export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    confirmed: 'Подтверждён',
    preparing: 'Готовится',
    delivering: 'В пути',
    delivered: 'Доставлен',
    cancelled: 'Отменён',
  };
  return labels[status] || status;
}

/**
 * Helper to format status for timeline steps
 */
export interface TimelineStep {
  key: string;
  label: string;
  completed: boolean;
  active: boolean;
}

export function getOrderTimeline(status: string): TimelineStep[] {
  const steps = ['confirmed', 'preparing', 'delivering', 'delivered'];
  const currentStepIndex = steps.indexOf(status);

  return [
    {
      key: 'confirmed',
      label: 'Заказ подтверждён',
      completed: currentStepIndex >= 0,
      active: currentStepIndex === 0,
    },
    {
      key: 'preparing',
      label: 'Букет готов',
      completed: currentStepIndex >= 1,
      active: currentStepIndex === 1,
    },
    {
      key: 'delivering',
      label: 'Передан курьеру',
      completed: currentStepIndex >= 2,
      active: currentStepIndex === 2,
    },
    {
      key: 'delivered',
      label: 'Доставлен',
      completed: currentStepIndex >= 3,
      active: currentStepIndex === 3,
    },
  ];
}
