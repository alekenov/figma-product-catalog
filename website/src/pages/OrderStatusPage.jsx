import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { fetchOrderStatus } from '../services/api';
import Header from '../components/layout/Header';
import OrderProgressBar from '../components/OrderProgressBar';
import OrderPhotoGallery from '../components/OrderPhotoGallery';
import OrderLineItems from '../components/OrderLineItems';
import CvetyButton from '../components/ui/CvetyButton';
import CvetyToggle from '../components/ui/cvety-toggle';
import { CvetyCard, CvetyCardContent, CvetyCardHeader, CvetyCardTitle } from '../components/ui/cvety-card';

// Компонент для строки информации (label + value)
function InfoRow({ label, value }) {
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
  const { orderNumber } = useParams();
  const [yandexDelivery, setYandexDelivery] = useState(false);
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadOrderStatus() {
      try {
        setLoading(true);
        const data = await fetchOrderStatus(orderNumber);
        setOrderData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load order status:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (orderNumber) {
      loadOrderStatus();
    }
  }, [orderNumber]);

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
        <main className="flex-1 px-4 py-4 flex items-center justify-center">
          <p className="font-sans text-body-1 text-text-black">
            Ошибка загрузки заказа: {error || 'Заказ не найден'}
          </p>
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
              Заказ {orderData.order_number} в пути
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
              label="Получатель"
              value={`${orderData.recipient.name}, ${orderData.recipient.phone}`}
            />
            <InfoRow
              label="Адрес самовывоза"
              value={orderData.pickup_address}
            />
            <InfoRow
              label="Адрес доставки"
              value={orderData.delivery_address}
            />
            <InfoRow
              label="Дата и время"
              value={orderData.date_time}
            />
            <InfoRow
              label="Отправитель"
              value={orderData.sender.phone}
            />
          </CvetyCardContent>
        </CvetyCard>

        {/* Photo Section */}
        <CvetyCard>
          <SectionHeader title="Фото заказа" />
          <CvetyCardContent>
            <OrderPhotoGallery photos={orderData.photos} />
          </CvetyCardContent>
        </CvetyCard>

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
          <CvetyButton variant="primary" size="md" fullWidth>
            Добавить комментарий
          </CvetyButton>
          <CvetyButton variant="secondary" size="md" fullWidth>
            Редактировать заказ
          </CvetyButton>
          <CvetyButton variant="secondary" size="md" fullWidth>
            Отменить заказ
          </CvetyButton>
        </div>
      </main>
    </div>
  );
}
