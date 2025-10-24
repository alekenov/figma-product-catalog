import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOrderStatus } from './useOrderStatus';
import * as services from '../../../services';
import React from 'react';

// Mock ToastProvider
const mockShowSuccess = vi.fn();
vi.mock('../../../components/ToastProvider', () => ({
  useToast: () => ({ showSuccess: mockShowSuccess })
}));

// Mock services
vi.mock('../../../services', () => ({
  ordersAPI: {
    updateOrderStatus: vi.fn()
  }
}));

// Mock window.confirm
global.confirm = vi.fn();

describe('useOrderStatus', () => {
  let mockOrderData;
  let mockOnSuccess;

  beforeEach(() => {
    vi.clearAllMocks();
    mockShowSuccess.mockClear();
    global.confirm.mockReturnValue(true);

    mockOrderData = {
      id: 1,
      status: 'new',
      orderNumber: 'ORD-001'
    };

    mockOnSuccess = vi.fn();
  });

  it('should initialize with correct available statuses', () => {
    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    expect(result.current.availableStatuses).toHaveLength(7);
    expect(result.current.availableStatuses[0]).toEqual({ id: 'new', label: 'Новый' });
  });

  it('should correctly determine next status', () => {
    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    expect(result.current.getNextStatus('new')).toBe('accepted');
    expect(result.current.getNextStatus('paid')).toBe('accepted');
    expect(result.current.getNextStatus('accepted')).toBe('assembled');
    expect(result.current.getNextStatus('assembled')).toBe('in_delivery');
    expect(result.current.getNextStatus('in_delivery')).toBe('delivered');
    expect(result.current.getNextStatus('delivered')).toBe(null);
    expect(result.current.getNextStatus('cancelled')).toBe(null);
  });

  it('should provide correct next status button text', () => {
    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    expect(result.current.getNextStatusButtonText('new')).toBe('Принять заказ');
    expect(result.current.getNextStatusButtonText('paid')).toBe('Принять заказ');
    expect(result.current.getNextStatusButtonText('accepted')).toBe('Собрать');
    expect(result.current.getNextStatusButtonText('assembled')).toBe('Передать курьеру');
    expect(result.current.getNextStatusButtonText('in_delivery')).toBe('Доставлен');
    expect(result.current.getNextStatusButtonText('delivered')).toBe(null);
  });

  it('should toggle status dropdown', () => {
    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    expect(result.current.isStatusDropdownOpen).toBe(false);

    act(() => {
      result.current.setIsStatusDropdownOpen(true);
    });

    expect(result.current.isStatusDropdownOpen).toBe(true);
  });

  it('should handle successful status change', async () => {
    services.ordersAPI.updateOrderStatus.mockResolvedValue({});

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    await act(async () => {
      await result.current.handleStatusChange('accepted');
    });

    expect(services.ordersAPI.updateOrderStatus).toHaveBeenCalledWith(1, 'accepted');
    expect(result.current.isStatusDropdownOpen).toBe(false);
    expect(mockShowSuccess).toHaveBeenCalledWith('Статус заказа изменен на "Принят"');
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('should handle next status progression', async () => {
    services.ordersAPI.updateOrderStatus.mockResolvedValue({});

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    await act(async () => {
      await result.current.handleNextStatus();
    });

    expect(services.ordersAPI.updateOrderStatus).toHaveBeenCalledWith(1, 'accepted');
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('should handle order cancellation with confirmation', async () => {
    global.confirm.mockReturnValue(true);
    services.ordersAPI.updateOrderStatus.mockResolvedValue({});

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    await act(async () => {
      await result.current.handleCancelOrder();
    });

    expect(global.confirm).toHaveBeenCalledWith('Отменить заказ?');
    expect(services.ordersAPI.updateOrderStatus).toHaveBeenCalledWith(1, 'cancelled');
    expect(mockShowSuccess).toHaveBeenCalledWith('Статус заказа изменен на "Отменен"');
  });

  it('should not cancel order if user declines confirmation', async () => {
    global.confirm.mockReturnValue(false);

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    await act(async () => {
      await result.current.handleCancelOrder();
    });

    expect(services.ordersAPI.updateOrderStatus).not.toHaveBeenCalled();
  });

  it('should handle API errors gracefully', async () => {
    services.ordersAPI.updateOrderStatus.mockRejectedValue(new Error('Network error'));
    global.alert = vi.fn();

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    await act(async () => {
      await result.current.handleStatusChange('accepted');
    });

    expect(global.alert).toHaveBeenCalledWith('Не удалось изменить статус заказа');
    expect(result.current.isUpdatingStatus).toBe(false);
  });

  it('should prevent concurrent status updates', async () => {
    services.ordersAPI.updateOrderStatus.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    const { result } = renderHook(() => useOrderStatus(mockOrderData, mockOnSuccess));

    // Start first update
    act(() => {
      result.current.handleStatusChange('accepted');
    });

    // Try second update immediately
    await act(async () => {
      await result.current.handleStatusChange('assembled');
    });

    // Should only be called once (first call)
    expect(services.ordersAPI.updateOrderStatus).toHaveBeenCalledTimes(1);
  });

  it('should do nothing if orderData is null', async () => {
    const { result } = renderHook(() => useOrderStatus(null, mockOnSuccess));

    await act(async () => {
      await result.current.handleStatusChange('accepted');
    });

    expect(services.ordersAPI.updateOrderStatus).not.toHaveBeenCalled();
  });
});
