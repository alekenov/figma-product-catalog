import { useState } from 'react';
import { ordersAPI } from '../../../services';
import { useToast } from '../../../components/ToastProvider';

export const useOrderStatus = (orderData, onSuccess) => {
  const { showSuccess } = useToast();
  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const availableStatuses = [
    { id: 'new', label: 'Новый' },
    { id: 'paid', label: 'Оплачен' },
    { id: 'accepted', label: 'Принят' },
    { id: 'assembled', label: 'Собран' },
    { id: 'in_delivery', label: 'В доставке' },
    { id: 'delivered', label: 'Доставлен' },
    { id: 'cancelled', label: 'Отменен' }
  ];

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      'new': 'accepted',
      'paid': 'accepted',
      'accepted': 'assembled',
      'assembled': 'in_delivery',
      'in_delivery': 'delivered',
      'delivered': null,
      'cancelled': null
    };
    return statusFlow[currentStatus] || null;
  };

  const getNextStatusButtonText = (currentStatus) => {
    const buttonTexts = {
      'new': 'Принять заказ',
      'paid': 'Принять заказ',
      'accepted': 'Собрать',
      'assembled': 'Передать курьеру',
      'in_delivery': 'Доставлен'
    };
    return buttonTexts[currentStatus] || null;
  };

  const handleStatusChange = async (newStatus) => {
    if (!orderData || isUpdatingStatus) return;

    try {
      setIsUpdatingStatus(true);

      await ordersAPI.updateOrderStatus(orderData.id, newStatus);

      // Close dropdown
      setIsStatusDropdownOpen(false);

      // Show success message
      const newStatusLabel = availableStatuses.find(s => s.id === newStatus)?.label || newStatus;
      showSuccess(`Статус заказа изменен на "${newStatusLabel}"`);

      // Refresh order data
      if (onSuccess) await onSuccess();

    } catch (err) {
      console.error('Failed to update order status:', err);
      alert('Не удалось изменить статус заказа');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleNextStatus = async () => {
    if (!orderData) return;

    const nextStatus = getNextStatus(orderData.status);
    if (nextStatus) {
      await handleStatusChange(nextStatus);
    }
  };

  const handleCancelOrder = async () => {
    if (!confirm('Отменить заказ?')) return;
    await handleStatusChange('cancelled');
  };

  return {
    availableStatuses,
    isStatusDropdownOpen,
    setIsStatusDropdownOpen,
    isUpdatingStatus,
    getNextStatus,
    getNextStatusButtonText,
    handleStatusChange,
    handleNextStatus,
    handleCancelOrder
  };
};
