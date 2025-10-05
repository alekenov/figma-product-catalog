import { Header } from './Header';
import { MinimalFooter } from './MinimalFooter';
import { OrderDetails } from './OrderDetails';
import { OrderItems } from './OrderItems';
import { OrderTracking } from './OrderTracking';
import { OrderActions } from './OrderActions';
import { useState } from 'react';

interface OrderStatusPageProps {
  orderId?: string;
}

function OrderHeader({ orderId = "70834" }: { orderId?: string }) {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <div className="space-y-[var(--spacing-2)]">
        <h1 className="text-[var(--text-primary)] font-medium">
          Заказ {orderId} в пути
        </h1>
        <p className="text-[var(--text-secondary)]">
          Ваш заказ обрабатывается и скоро будет доставлен
        </p>
      </div>
    </div>
  );
}

export function OrderStatusPage({ orderId }: OrderStatusPageProps) {
  const [orderDetailsRef, setOrderDetailsRef] = useState<any>(null);

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header />
        
        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
          <OrderHeader orderId={orderId} />
          <OrderTracking />
          <OrderDetails isEditable={true} />
          <OrderItems canEdit={true} />
          <OrderActions onEditOrder={() => console.log('Edit order')} />
        </div>
        
        <MinimalFooter />
      </div>
    </div>
  );
}