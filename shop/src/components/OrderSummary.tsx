import { CvetyButton } from './ui/cvety-button';
import { DeliveryMethod } from './DeliveryMethodSelector';
import { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8014/api/v1';

interface OrderSummaryProps {
  deliveryMethod: DeliveryMethod;
}

export function OrderSummary({ deliveryMethod }: OrderSummaryProps) {
  const deliveryCost = deliveryMethod === 'delivery' ? 1500 : 0;
  const deliveryText = deliveryMethod === 'delivery' ? 'Доставка' : 'Самовывоз';
  const deliveryCostText = deliveryMethod === 'delivery' ? '1 500 ₸' : 'Бесплатно';
  const totalCost = 193000 + deliveryCost;

  return (
    <div className="space-y-[var(--spacing-3)]">
      <div className="flex justify-between">
        <p className="text-body text-[var(--text-primary)]">Товаров на сумму</p>
        <p className="text-body text-[var(--text-primary)]">193 000 ₸</p>
      </div>

      <div className="flex justify-between border-b border-[var(--border)] pb-[var(--spacing-3)]">
        <p className="text-body text-[var(--text-primary)]">{deliveryText}</p>
        <p className="text-body text-[var(--text-primary)]">{deliveryCostText}</p>
      </div>

      <div className="flex justify-between">
        <p className="text-body-emphasis text-[var(--text-primary)]">Итого</p>
        <p className="text-price text-[var(--text-primary)]">{totalCost.toLocaleString()} ₸</p>
      </div>
    </div>
  );
}

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface CheckoutButtonProps {
  deliveryMethod: DeliveryMethod;
  onNavigate?: (page: PageType, data?: { storeId?: string; productId?: string; orderId?: string }) => void;
}

export function CheckoutButton({ deliveryMethod, onNavigate }: CheckoutButtonProps) {
  const totalCost = deliveryMethod === 'delivery' ? 194500 : 193000;
  const [isCreating, setIsCreating] = useState(false);

  const handleCheckout = async () => {
    setIsCreating(true);

    try {
      // Тестовые данные заказа
      const orderData = {
        customerName: "Тестовый покупатель",
        phone: "77015211545",
        customer_email: "test@example.com",
        delivery_address: deliveryMethod === 'delivery' ? "г. Астана, ул. Достык 3" : null,
        delivery_cost: deliveryMethod === 'delivery' ? 1500 : 0,
        delivery_notes: "Тестовый заказ из Shop",
        notes: "Создано через публичный shop интерфейс",
        recipient_name: "Иван Иванов",
        recipient_phone: "77771234567",
        items: [
          {
            product_id: 1,
            quantity: 2,
            special_requests: "Без доп. упаковки"
          }
        ],
        check_availability: false
      };

      const response = await fetch(`${API_BASE_URL}/orders/public/create?shop_id=11`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка создания заказа');
      }

      const createdOrder = await response.json();
      console.log('Заказ создан:', createdOrder);

      // Переход на страницу статуса заказа
      if (onNavigate) {
        onNavigate('order-status', { orderId: createdOrder.id.toString() });
      }

    } catch (error: any) {
      console.error('Ошибка при создании заказа:', error);
      alert(`Не удалось создать заказ: ${error.message}`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <CvetyButton
      variant="primary"
      fullWidth
      size="lg"
      onClick={handleCheckout}
      disabled={isCreating}
    >
      {isCreating ? 'Создание заказа...' : `Оформить заказ за ${totalCost.toLocaleString()} ₸`}
    </CvetyButton>
  );
}