import React from 'react';
import { useOrder } from './OrderContext';
import InfoRow from '../InfoRow';

const OrderInfo = () => {
  const { orderData, recipientInfo } = useOrder();

  if (!orderData) return null;

  const handleCopyTrackingLink = async () => {
    const trackingLink = `${window.location.origin}/order-status/${orderData.tracking_id}`;
    try {
      await navigator.clipboard.writeText(trackingLink);
      alert('Ссылка для отслеживания скопирована в буфер обмена');
    } catch (err) {
      console.error('Failed to copy tracking link:', err);
      alert('Не удалось скопировать ссылку');
    }
  };

  return (
    <div className="bg-white rounded-lg p-4 mb-4">
      <h2 className="text-lg font-semibold mb-4">Информация о заказе</h2>

      <div className="space-y-3">
        <InfoRow label="Номер заказа" value={orderData.orderNumber} />

        <InfoRow
          label="Tracking ID"
          value={orderData.tracking_id}
          action={
            <button
              onClick={handleCopyTrackingLink}
              className="text-purple-primary hover:underline text-sm"
            >
              Скопировать ссылку
            </button>
          }
        />

        <InfoRow label="Дата создания" value={orderData.created_at} />

        <InfoRow label="Заказчик" value={orderData.customerName} />

        <InfoRow label="Телефон" value={orderData.phone} />

        {orderData.delivery_type === 'delivery' ? (
          <InfoRow label="Адрес доставки" value={orderData.delivery_address} />
        ) : (
          <InfoRow label="Адрес самовывоза" value={orderData.pickup_address} />
        )}

        <InfoRow label="Дата доставки" value={orderData.delivery_date} />

        {orderData.delivery_time && (
          <InfoRow label="Время доставки" value={orderData.delivery_time} />
        )}

        {recipientInfo && (
          <>
            <InfoRow label="Получатель" value={recipientInfo.name} />
            <InfoRow label="Телефон получателя" value={recipientInfo.phone} />
          </>
        )}

        {orderData.notes && (
          <div className="border-t pt-3 mt-3">
            <div className="text-sm text-gray-disabled mb-1">Комментарий:</div>
            <div className="text-sm whitespace-pre-wrap">{orderData.notes}</div>
          </div>
        )}

        <InfoRow label="Способ оплаты" value={orderData.payment_method === 'cash' ? 'Наличные' : orderData.payment_method === 'kaspi' ? 'Kaspi Pay' : orderData.payment_method} />
      </div>
    </div>
  );
};

export default OrderInfo;
