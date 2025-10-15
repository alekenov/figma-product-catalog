import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { Header } from './Header';
import { MinimalFooter } from './MinimalFooter';
import { OrderDetails } from './OrderDetails';
import { OrderItems } from './OrderItems';
import { OrderTracking } from './OrderTracking';
import { OrderActions } from './OrderActions';
import { KaspiPaymentStatus } from './KaspiPaymentStatus';
import { fetchOrderByTrackingId, OrderStatusResponse } from '../services/orderApi';

function OrderHeader({ orderNumber, status }: { orderNumber?: string; status?: string }) {
  const getStatusMessage = (status?: string): string => {
    switch (status) {
      case 'confirmed': return 'в обработке';
      case 'preparing': return 'готовится';
      case 'delivering': return 'в пути';
      case 'delivered': return 'доставлен';
      case 'cancelled': return 'отменён';
      default: return 'обрабатывается';
    }
  };

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <div className="space-y-[var(--spacing-2)]">
        <h1 className="text-[var(--text-primary)] font-medium">
          Заказ {orderNumber || '...'} {getStatusMessage(status)}
        </h1>
        <p className="text-[var(--text-secondary)]">
          Ваш заказ обрабатывается и скоро будет доставлен
        </p>
      </div>
    </div>
  );
}

export function OrderStatusPage() {
  const navigate = useNavigate();
  const { shopSlug, trackingId } = useParams();
  const { itemCount } = useCart();
  const [orderData, setOrderData] = useState<OrderStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const handleNavigate = (page: string) => {
    if (page === 'home') {
      navigate(`/${shopSlug}`);
    } else if (page === 'cart') {
      navigate(`/${shopSlug}/cart`);
    }
  };

  // Load order data by tracking ID
  useEffect(() => {
    async function loadOrder() {
      if (!trackingId) {
        setIsLoading(false);
        setError(new Error('Tracking ID not provided'));
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchOrderByTrackingId(trackingId);
        setOrderData(data);
      } catch (err) {
        console.error('[OrderStatusPage] Failed to load order:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }

    loadOrder();
  }, [trackingId]);

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-[var(--background-secondary)] min-h-screen">
        <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
          <div className="px-[var(--spacing-4)]">
            <Header onNavigate={handleNavigate} itemCount={itemCount} />
          </div>
          <div className="p-[var(--spacing-4)] flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--brand-primary)] mx-auto mb-4"></div>
              <p className="text-[var(--text-secondary)]">Загрузка заказа...</p>
            </div>
          </div>
          <MinimalFooter />
        </div>
      </div>
    );
  }

  // Error state
  if (error || !orderData) {
    return (
      <div className="bg-[var(--background-secondary)] min-h-screen">
        <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
          <div className="px-[var(--spacing-4)]">
            <Header onNavigate={handleNavigate} itemCount={itemCount} />
          </div>
          <div className="p-[var(--spacing-4)] flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="text-6xl mb-4">❌</div>
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                Заказ не найден
              </h2>
              <p className="text-[var(--text-secondary)] mb-4">
                {error?.message || 'Проверьте код отслеживания'}
              </p>
            </div>
          </div>
          <MinimalFooter />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <div className="px-[var(--spacing-4)]">
          <Header onNavigate={handleNavigate} itemCount={itemCount} />
        </div>

        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
          <OrderHeader orderNumber={orderData.order_number} status={orderData.status} />
          <OrderTracking status={orderData.status} photos={orderData.photos} trackingId={trackingId} />

          {/* Show Kaspi payment status if payment method is kaspi */}
          {orderData.payment_method === 'kaspi' && orderData.kaspi_payment_id && (
            <KaspiPaymentStatus
              phone={orderData.sender.phone}
              status={orderData.kaspi_payment_status}
              externalId={orderData.kaspi_payment_id}
            />
          )}

          <OrderDetails
            isEditable={true}
            trackingId={trackingId}
            orderData={orderData}
          />
          <OrderItems
            canEdit={false}
            items={orderData.items}
            deliveryCost={orderData.delivery_cost}
            total={orderData.total}
          />
          <OrderActions onEditOrder={() => console.log('Edit order')} />
        </div>

        <MinimalFooter />
      </div>
    </div>
  );
}