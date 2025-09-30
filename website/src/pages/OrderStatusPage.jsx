import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
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
  const [yandexDelivery, setYandexDelivery] = useState(false);

  // Данные заказа из localStorage или mock
  const getOrderData = () => {
    const savedOrder = localStorage.getItem('cvety_current_order');
    if (savedOrder) {
      return JSON.parse(savedOrder);
    }

    // Mock данные как fallback
    return {
      orderId: '70834',
      status: 'delivering', // confirmed | preparing | delivering
      recipient: {
        name: 'Ксения',
        phone: '+7 (917) 096-5427'
      },
      pickupAddress: 'г. Астана, ул. Достык, 5',
      deliveryAddress: 'г. Астана, ул. Сарайшык, 127',
      dateTime: 'Понедельник 30 января, 14:24',
      sender: {
        phone: '+7 (964) 796-8760'
      },
      photos: [
        {
          url: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400',
          label: 'Букет на витрине'
        },
        {
          url: 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400',
          label: 'Собран для вас'
        }
      ],
      items: [
        { name: 'Букет розовых пионов', price: 23500 },
        { name: 'Упаковочная лента и бумага', price: 0 },
        { name: 'Электронный сертификат в SPA от 1 часа', price: 20000 }
      ],
      deliveryCost: 0,
      deliveryType: 'Самовывоз',
      total: 43500,
      bonusPoints: 985
    };
  };

  const orderData = getOrderData();

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
              Заказ {orderData.orderId} в пути
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
              value={orderData.pickupAddress}
            />
            <InfoRow
              label="Адрес доставки"
              value={orderData.deliveryAddress}
            />
            <InfoRow
              label="Дата и время"
              value={orderData.dateTime}
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
              deliveryCost={orderData.deliveryCost}
              deliveryType={orderData.deliveryType}
              total={orderData.total}
              bonusPoints={orderData.bonusPoints}
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
