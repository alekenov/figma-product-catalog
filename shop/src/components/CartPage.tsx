import { Header } from './Header';
import { MinimalFooter } from './MinimalFooter';
import { CartHeader } from './CartHeader';
import { CartItems } from './CartItems';
import { CardAddOn } from './CardAddOn';
import { OrderForms } from './OrderForms';
import { OrderSummary, CheckoutButton } from './OrderSummary';
import { DeliveryTimeSelector } from './DeliveryTimeSelector';
import { DeliveryMethod } from './DeliveryMethodSelector';
import { useState } from 'react';

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface CartPageProps {
  onNavigate?: (page: PageType, data?: { storeId?: string; productId?: string; orderId?: string }) => void;
}

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

export function CartPage({ onNavigate }: CartPageProps) {
  const [deliveryMethod, setDeliveryMethod] = useState<DeliveryMethod>('delivery');

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header onNavigate={onNavigate} />

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

          <CheckoutButton deliveryMethod={deliveryMethod} onNavigate={onNavigate} />
        </div>

        <MinimalFooter />
      </div>
    </div>
  );
}