import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { fetchOrderByTrackingId, submitPhotoFeedback } from '../services/api';
import Header from '../components/layout/Header';
import OrderProgressBar from '../components/OrderProgressBar';
import OrderPhotoGallery from '../components/OrderPhotoGallery';
import OrderLineItems from '../components/OrderLineItems';
import CvetyButton from '../components/ui/CvetyButton';
import CvetyToggle from '../components/ui/cvety-toggle';
import { CvetyCard, CvetyCardContent, CvetyCardHeader, CvetyCardTitle } from '../components/ui/cvety-card';

// Компонент для строки информации (label + value)
function InfoRow({ label, value, isEditable, fieldName, editValue, onEditChange }) {
  if (isEditable) {
    return (
      <div className="space-y-2">
        <label htmlFor={fieldName} className="font-sans font-normal text-[14px] leading-[1.4] text-text-grey-dark">
          {label}
        </label>
        <input
          id={fieldName}
          type="text"
          value={editValue || ''}
          onChange={(e) => onEditChange(fieldName, e.target.value)}
          className="w-full px-3 py-2 font-sans font-normal text-[14px] leading-[1.4] text-text-black border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink"
        />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="font-sans font-normal text-[14px] leading-[1.4] text-text-grey-dark">
        {label}
      </p>
      <p className="font-sans font-normal text-[14px] leading-[1.4] text-text-black">
        {value}
      </p>
    </div>
  );
}

// Компонент для заголовка секции
function SectionHeader({ title }) {
  return (
    <CvetyCardHeader className="bg-bg-secondary">
      <CvetyCardTitle className="!text-body-1 !font-semibold text-text-black">
        {title}
      </CvetyCardTitle>
    </CvetyCardHeader>
  );
}

export default function OrderStatusPage() {
  const { getCartCount } = useCart();
  const { id: trackingId } = useParams(); // URL param is now tracking_id
  const [yandexDelivery, setYandexDelivery] = useState(false);
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit mode state
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [isSaving, setIsSaving] = useState(false);

  // Photo feedback state
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // Check if order can be edited based on status
  const canEditOrder = () => {
    if (!orderData) return false;
    // Use frontend status values (mapped from backend)
    const editableStatuses = ['new', 'paid', 'confirmed', 'preparing', 'delivering'];
    return editableStatuses.includes(orderData.status);
  };

  // Handle field changes in edit mode
  const handleFieldChange = (fieldName, value) => {
    setEditedData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Toggle edit mode
  const handleEditToggle = () => {
    if (!isEditMode) {
      // Entering edit mode - initialize editedData with current values
      setEditedData({
        recipient_name: orderData.recipient.name || '',
        recipient_phone: orderData.recipient.phone || '',
        pickup_address: orderData.pickup_address || '',
        delivery_address: orderData.delivery_address || '',
        sender_phone: orderData.sender.phone || '',
      });
    }
    setIsEditMode(!isEditMode);
  };

  // Save changes
  const handleSaveChanges = async () => {
    try {
      setIsSaving(true);

      // Call API to update order
      const response = await fetch(
        `http://localhost:8014/api/v1/orders/by-tracking/${trackingId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(editedData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update order');
      }

      // Refresh order data
      const updatedData = await fetchOrderByTrackingId(trackingId);
      setOrderData(updatedData);
      setIsEditMode(false);
      setError(null);
      alert('Заказ успешно обновлен!');
    } catch (err) {
      console.error('Failed to save order changes:', err);
      setError(err.message);
      alert(`Ошибка сохранения: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setIsEditMode(false);
    setEditedData({});
  };

  // Handle photo feedback submission
  const handleFeedbackSubmit = async (feedback, comment) => {
    try {
      // Use tracking_id directly
      await submitPhotoFeedback(trackingId, feedback, comment);

      // Mark feedback as submitted
      setFeedbackSubmitted(true);

      // Refresh order data to get updated feedback
      const updatedData = await fetchOrderByTrackingId(trackingId);
      setOrderData(updatedData);

    } catch (err) {
      console.error('Failed to submit feedback:', err);
      alert(`Ошибка отправки отзыва: ${err.message}`);
      throw err; // Re-throw to let component handle it
    }
  };

  useEffect(() => {
    async function loadOrderStatus() {
      try {
        setLoading(true);
        const data = await fetchOrderByTrackingId(trackingId);
        setOrderData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load order status:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (trackingId) {
      loadOrderStatus();

      // Auto-refresh every 30 seconds to check for status updates
      const refreshInterval = setInterval(() => {
        // Silent refresh without showing loading state
        fetchOrderByTrackingId(trackingId)
          .then(data => {
            setOrderData(data);
            setError(null);
          })
          .catch(err => {
            console.error('Failed to refresh order status:', err);
            // Don't update error state to avoid disrupting user experience
          });
      }, 30000); // 30 seconds

      // Cleanup interval on unmount
      return () => clearInterval(refreshInterval);
    }
  }, [trackingId]);

  if (loading) {
    return (
      <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
        <Header cartCount={getCartCount()} />
        <main className="flex-1 px-4 py-4 flex items-center justify-center">
          <p className="font-sans text-body-1 text-text-grey-dark">Загрузка заказа...</p>
        </main>
      </div>
    );
  }

  if (error || !orderData) {
    return (
      <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
        <Header cartCount={getCartCount()} />
        <main className="flex-1 px-4 py-8 flex flex-col items-center justify-center space-y-6">
          {/* Error Icon */}
          <div className="w-20 h-20 rounded-full bg-bg-light flex items-center justify-center">
            <svg
              className="w-10 h-10 text-text-grey-dark"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Error Message */}
          <div className="text-center space-y-2">
            <h1 className="font-sans font-semibold text-headline-2 text-text-black">
              Заказ не найден
            </h1>
            <p className="font-sans text-body-2 text-text-grey-dark max-w-xs">
              Проверьте правильность номера отслеживания или обратитесь в поддержку
            </p>
            {error && error !== 'Resource not found' && (
              <p className="font-sans text-caption text-text-grey-dark mt-2">
                Ошибка: {error}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="w-full space-y-2 pt-4">
            <CvetyButton
              variant="primary"
              size="md"
              fullWidth
              onClick={() => window.location.href = '/'}
            >
              На главную
            </CvetyButton>
            <CvetyButton
              variant="secondary"
              size="md"
              fullWidth
              onClick={() => window.location.href = 'tel:+77015211545'}
            >
              Связаться с поддержкой
            </CvetyButton>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      {/* Header */}
      <Header cartCount={getCartCount()} />

      {/* Main Content */}
      <main className="flex-1 px-4 py-4 space-y-4">
        {/* Order Status Card */}
        <CvetyCard>
          <CvetyCardContent className="space-y-4">
            <h1 className="font-sans font-semibold text-body-1 text-text-black">
              Заказ {orderData.tracking_id} в пути
            </h1>
            <OrderProgressBar currentStage={orderData.status} />
          </CvetyCardContent>
        </CvetyCard>

        {/* Yandex Delivery Toggle */}
        <CvetyCard>
          <CvetyCardContent>
            <CvetyToggle
              checked={yandexDelivery}
              onCheckedChange={setYandexDelivery}
              label="Заказать Яндекс доставку"
            />
          </CvetyCardContent>
        </CvetyCard>

        {/* Delivery Section */}
        <CvetyCard>
          <SectionHeader title="Доставка" />
          <CvetyCardContent className="space-y-4">
            <InfoRow
              label="Имя получателя"
              value={orderData.recipient.name}
              isEditable={isEditMode}
              fieldName="recipient_name"
              editValue={editedData.recipient_name}
              onEditChange={handleFieldChange}
            />
            <InfoRow
              label="Телефон получателя"
              value={orderData.recipient.phone}
              isEditable={isEditMode}
              fieldName="recipient_phone"
              editValue={editedData.recipient_phone}
              onEditChange={handleFieldChange}
            />
            <InfoRow
              label="Адрес самовывоза"
              value={orderData.pickup_address}
              isEditable={isEditMode}
              fieldName="pickup_address"
              editValue={editedData.pickup_address}
              onEditChange={handleFieldChange}
            />
            <InfoRow
              label="Адрес доставки"
              value={orderData.delivery_address}
              isEditable={isEditMode}
              fieldName="delivery_address"
              editValue={editedData.delivery_address}
              onEditChange={handleFieldChange}
            />
            <InfoRow
              label="Дата и время"
              value={orderData.date_time}
              isEditable={false}
            />
            <InfoRow
              label="Телефон отправителя"
              value={orderData.sender.phone}
              isEditable={isEditMode}
              fieldName="sender_phone"
              editValue={editedData.sender_phone}
              onEditChange={handleFieldChange}
            />
          </CvetyCardContent>
        </CvetyCard>

        {/* Photo Section - Only show if photos exist */}
        {orderData.photos && orderData.photos.length > 0 && (
          <CvetyCard>
            <SectionHeader title="Фото заказа" />
            <CvetyCardContent>
              <OrderPhotoGallery
                photos={orderData.photos}
                onFeedbackSubmit={handleFeedbackSubmit}
                feedbackSubmitted={feedbackSubmitted}
              />
            </CvetyCardContent>
          </CvetyCard>
        )}

        {/* Order Summary Section */}
        <CvetyCard>
          <SectionHeader title="Итого" />
          <CvetyCardContent>
            <OrderLineItems
              items={orderData.items}
              deliveryCost={orderData.delivery_cost}
              deliveryType={orderData.delivery_type}
              total={orderData.total}
              bonusPoints={orderData.bonus_points}
            />
          </CvetyCardContent>
        </CvetyCard>

        {/* Action Buttons */}
        <div className="space-y-2">
          {isEditMode ? (
            <>
              <CvetyButton
                variant="primary"
                size="md"
                fullWidth
                onClick={handleSaveChanges}
                disabled={isSaving}
              >
                {isSaving ? 'Сохранение...' : 'Сохранить изменения'}
              </CvetyButton>
              <CvetyButton
                variant="secondary"
                size="md"
                fullWidth
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                Отменить
              </CvetyButton>
            </>
          ) : (
            <>
              <CvetyButton variant="primary" size="md" fullWidth>
                Добавить комментарий
              </CvetyButton>
              <CvetyButton
                variant="secondary"
                size="md"
                fullWidth
                onClick={handleEditToggle}
                disabled={!canEditOrder()}
              >
                Редактировать заказ
              </CvetyButton>
              <CvetyButton variant="secondary" size="md" fullWidth>
                Отменить заказ
              </CvetyButton>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
