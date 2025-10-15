import { CvetyInput } from './ui/cvety-input';
import { CvetyTextarea } from './ui/cvety-textarea';
import { CvetyButton } from './ui/cvety-button';
import { useState, useEffect } from 'react';
import { updateOrderByTrackingId, OrderStatusResponse } from '../services/orderApi';

interface OrderDetailsProps {
  isEditable?: boolean;
  trackingId?: string;
  orderData?: OrderStatusResponse;
}

export function OrderDetails({ isEditable = true, trackingId, orderData }: OrderDetailsProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Parse date_time from API (format: "2024-10-14T14:24:00")
  const parseDateTime = (dateTimeStr: string) => {
    if (!dateTimeStr) return { date: '', time: '' };
    const dt = new Date(dateTimeStr);
    const date = dt.toISOString().split('T')[0]; // YYYY-MM-DD
    const time = dt.toTimeString().slice(0, 5); // HH:MM
    return { date, time };
  };

  // Initialize editData from orderData
  const { date: parsedDate, time: parsedTime } = orderData?.date_time
    ? parseDateTime(orderData.date_time)
    : { date: '', time: '' };

  const [editData, setEditData] = useState({
    recipient: orderData?.recipient?.name || '',
    phone: orderData?.recipient?.phone || '',
    address: orderData?.delivery_address || '',
    deliveryDate: parsedDate,
    deliveryTime: parsedTime,
    comment: '', // Note: не приходит из API, будем хранить локально
    cardText: '' // Note: не приходит из API, будем хранить локально
  });

  const [originalData, setOriginalData] = useState(editData);

  // Update editData when orderData changes
  useEffect(() => {
    if (orderData) {
      const { date, time } = parseDateTime(orderData.date_time);
      const newData = {
        recipient: orderData.recipient?.name || '',
        phone: orderData.recipient?.phone || '',
        address: orderData.delivery_address || '',
        deliveryDate: date,
        deliveryTime: time,
        comment: editData.comment, // Keep existing comment
        cardText: editData.cardText // Keep existing card text
      };
      setEditData(newData);
      setOriginalData(newData);
    }
  }, [orderData]);

  // Determine if order can be edited based on status
  const canEdit = isEditable && orderData?.status !== 'delivering' && orderData?.status !== 'delivered';

  const handleSave = async () => {
    if (!trackingId) {
      alert('Ошибка: отсутствует tracking ID');
      return;
    }

    setIsSaving(true);

    try {
      // Combine date and time for API
      const deliveryDateTime = `${editData.deliveryDate}T${editData.deliveryTime}:00`;

      await updateOrderByTrackingId(trackingId, {
        recipient_name: editData.recipient,
        delivery_address: editData.address,
        delivery_date: editData.deliveryDate,
        delivery_time: editData.deliveryTime,
        notes: editData.comment || undefined,
        delivery_notes: editData.cardText || undefined
      });

      setOriginalData(editData);
      setIsEditing(false);
      alert('✅ Заказ успешно обновлен!');
    } catch (error) {
      console.error('Failed to update order:', error);
      alert('❌ Не удалось обновить заказ. Попробуйте позже.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditData(originalData);
    setIsEditing(false);
  };

  const orderInfo = [
    {
      key: 'recipient',
      label: 'Получатель',
      value: `${editData.recipient}, ${editData.phone}`,
      editable: true
    },
    {
      key: 'address',
      label: 'Адрес доставки',
      value: editData.address || 'Не указан',
      editable: true
    },
    {
      key: 'datetime',
      label: 'Дата и время',
      value: editData.deliveryDate && editData.deliveryTime
        ? `${new Date(editData.deliveryDate).toLocaleDateString('ru-RU', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}, ${editData.deliveryTime}`
        : 'Не указано',
      editable: true
    },
    {
      key: 'comment',
      label: 'Комментарий к заказу',
      value: editData.comment || 'Нет комментария',
      editable: true
    },
    {
      key: 'cardText',
      label: 'Текст открытки',
      value: editData.cardText || 'Нет текста открытки',
      editable: true
    }
  ];

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <div className="flex items-center justify-between">
        <h2 className="text-[var(--text-primary)] font-medium">Детали заказа</h2>

        {canEdit && !isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] text-sm font-medium hover:bg-[var(--brand-primary)]/5 transition-colors"
          >
            Редактировать
          </button>
        )}
      </div>

      {!canEdit && (
        <div className="p-[var(--spacing-3)] bg-[var(--background-secondary)] rounded-[var(--radius-md)]">
          <p className="text-[var(--text-secondary)] text-sm">
            ⚠️ Заказ нельзя изменить, так как он уже {orderData?.status === 'delivering' ? 'передан курьеру' : 'доставлен'}
          </p>
        </div>
      )}

      <div className="space-y-[var(--spacing-4)]">
        {!isEditing ? (
          <div className="space-y-[var(--spacing-3)]">
            {orderInfo.map((info, index) => (
              <div key={index} className="space-y-[var(--spacing-1)]">
                <p className="text-[var(--text-secondary)] text-sm">{info.label}</p>
                <p className="text-[var(--text-primary)]">{info.value}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-[var(--spacing-4)]">
            <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
              <CvetyInput
                label="Имя получателя"
                value={editData.recipient}
                onChange={(e) => setEditData({...editData, recipient: e.target.value})}
              />
              <CvetyInput
                label="Телефон"
                value={editData.phone}
                onChange={(e) => setEditData({...editData, phone: e.target.value})}
              />
            </div>

            <CvetyInput
              label="Адрес доставки"
              value={editData.address}
              onChange={(e) => setEditData({...editData, address: e.target.value})}
            />

            <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
              <CvetyInput
                label="Дата доставки"
                type="date"
                value={editData.deliveryDate}
                onChange={(e) => setEditData({...editData, deliveryDate: e.target.value})}
              />
              <CvetyInput
                label="Время доставки"
                type="time"
                value={editData.deliveryTime}
                onChange={(e) => setEditData({...editData, deliveryTime: e.target.value})}
              />
            </div>

            <CvetyInput
              label="Комментарий к заказу"
              value={editData.comment}
              onChange={(e) => setEditData({...editData, comment: e.target.value})}
            />

            <CvetyTextarea
              label="Текст открытки"
              value={editData.cardText}
              onChange={(e) => setEditData({...editData, cardText: e.target.value})}
              className="min-h-[80px]"
            />

            <div className="flex gap-[var(--spacing-3)]">
              <CvetyButton
                variant="primary"
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1"
              >
                {isSaving ? 'Сохранение...' : 'Сохранить'}
              </CvetyButton>
              <CvetyButton
                variant="secondary"
                onClick={handleCancel}
                disabled={isSaving}
                className="flex-1"
              >
                Отменить
              </CvetyButton>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
