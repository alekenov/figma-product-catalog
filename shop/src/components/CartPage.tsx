import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { Header } from './Header';
import { MinimalFooter } from './MinimalFooter';
import { CartHeader } from './CartHeader';
import { CartItems } from './CartItems';
import { CardAddOn } from './CardAddOn';
import { OrderForms } from './OrderForms';
import { OrderSummary, CheckoutButton } from './OrderSummary';
import { DeliveryTimeSelector } from './DeliveryTimeSelector';
import { DeliveryMethod } from './DeliveryMethodSelector';

function OrderFormSection({
  deliveryMethod,
  onDeliveryMethodChange
}: {
  deliveryMethod: DeliveryMethod;
  onDeliveryMethodChange: (method: DeliveryMethod) => void;
}) {
  const handleAddressSelect = () => {
    console.log('Выбор адреса');
  };

  return (
    <OrderForms
      deliveryMethod={deliveryMethod}
      onAddressSelect={handleAddressSelect}
    />
  );
}

export function CartPage() {
  const navigate = useNavigate();
  const { shopSlug } = useParams();
  const { itemCount } = useCart();
  const [deliveryMethod, setDeliveryMethod] = useState<DeliveryMethod>('delivery');

  const handleNavigate = (page: string, data?: any) => {
    if (page === 'order-status' && data?.trackingId) {
      navigate(`/${shopSlug}/order/${data.trackingId}`);
    } else if (page === 'home') {
      navigate(`/${shopSlug}`);
    } else if (page === 'cart') {
      navigate(`/${shopSlug}/cart`);
    }
  };

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <div className="px-[var(--spacing-4)]">
          <Header onNavigate={handleNavigate} itemCount={itemCount} />
        </div>

        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)] pb-[var(--spacing-8)]">
          <CartHeader
            deliveryMethod={deliveryMethod}
            onDeliveryMethodChange={setDeliveryMethod}
          />

          {/* Блок «дата и время» для самовывоза - показывается выше открытки */}
          {deliveryMethod === 'pickup' && <DeliveryTimeSelector />}

          <CardAddOn />

          <OrderFormSection
            deliveryMethod={deliveryMethod}
            onDeliveryMethodChange={setDeliveryMethod}
          />

          <CartItems />

          <OrderSummary deliveryMethod={deliveryMethod} />

          <CheckoutButton deliveryMethod={deliveryMethod} onNavigate={handleNavigate} />
        </div>

        <MinimalFooter />
      </div>
    </div>
  );
}