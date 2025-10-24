import React from 'react';
import { useOrder } from './OrderContext';
import { useOrderStatus } from './hooks/useOrderStatus';
import StatusBadge from '../StatusBadge';

const OrderStatusManager = () => {
  const { orderData, refreshOrder } = useOrder();
  const {
    availableStatuses,
    isStatusDropdownOpen,
    setIsStatusDropdownOpen,
    isUpdatingStatus,
    getNextStatusButtonText,
    handleStatusChange,
    handleNextStatus,
    handleCancelOrder
  } = useOrderStatus(orderData, refreshOrder);

  if (!orderData) return null;

  const nextStatusText = getNextStatusButtonText(orderData.status);
  const canCancel = orderData.status !== 'cancelled' && orderData.status !== 'delivered';

  return (
    <div className="bg-white rounded-lg p-4 mb-4">
      <h2 className="text-lg font-semibold mb-4">Статус заказа</h2>

      <div className="flex items-center gap-3 mb-4">
        <StatusBadge status={orderData.status} label={orderData.statusLabel} />

        {/* Status Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsStatusDropdownOpen(!isStatusDropdownOpen)}
            className="px-3 py-1 text-sm border border-gray-neutral rounded-md hover:bg-gray-50 transition-colors"
            disabled={isUpdatingStatus}
          >
            Изменить статус
          </button>

          {isStatusDropdownOpen && (
            <div className="absolute top-full left-0 mt-1 bg-white border border-gray-neutral rounded-md shadow-lg z-10 min-w-[200px]">
              {availableStatuses.map((status) => (
                <button
                  key={status.id}
                  onClick={() => handleStatusChange(status.id)}
                  className={`
                    block w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors
                    ${status.id === orderData.status ? 'bg-purple-50 font-semibold' : ''}
                  `}
                  disabled={isUpdatingStatus}
                >
                  {status.label}
                  {status.id === orderData.status && ' ✓'}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        {nextStatusText && (
          <button
            onClick={handleNextStatus}
            disabled={isUpdatingStatus}
            className="px-4 py-2 bg-purple-primary text-white text-sm rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {isUpdatingStatus ? 'Обновление...' : nextStatusText}
          </button>
        )}

        {canCancel && (
          <button
            onClick={handleCancelOrder}
            disabled={isUpdatingStatus}
            className="px-4 py-2 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors disabled:opacity-50"
          >
            Отменить заказ
          </button>
        )}
      </div>
    </div>
  );
};

export default OrderStatusManager;
