import { CvetyButton } from './ui/cvety-button';
import { DeliveryMethod } from './DeliveryMethodSelector';
import { useCart } from '../contexts/CartContext';
import { useShop } from '../contexts/ShopContext';
import { useOrderForm } from '../contexts/OrderFormContext';
import { useState } from 'react';
import { API_BASE_URL } from '../config/api';

interface OrderSummaryProps {
  deliveryMethod: DeliveryMethod;
}

export function OrderSummary({ deliveryMethod }: OrderSummaryProps) {
  const { subtotal, deliveryCost, total } = useCart();

  // Convert kopecks to tenge for display
  const subtotalTenge = Math.floor(subtotal / 100);
  const deliveryCostTenge = Math.floor(deliveryCost / 100);
  const totalTenge = Math.floor(total / 100);

  const deliveryText = deliveryMethod === 'delivery' ? 'Доставка' : 'Самовывоз';
  const deliveryCostText = deliveryCostTenge > 0 ? `${deliveryCostTenge.toLocaleString()} ₸` : 'Бесплатно';

  return (
    <div className="space-y-[var(--spacing-3)]">
      <div className="flex justify-between">
        <p className="text-body text-[var(--text-primary)]">Товаров на сумму</p>
        <p className="text-body text-[var(--text-primary)]">{subtotalTenge.toLocaleString()} ₸</p>
      </div>

      <div className="flex justify-between border-b border-[var(--border)] pb-[var(--spacing-3)]">
        <p className="text-body text-[var(--text-primary)]">{deliveryText}</p>
        <p className="text-body text-[var(--text-primary)]">{deliveryCostText}</p>
      </div>

      <div className="flex justify-between">
        <p className="text-body-emphasis text-[var(--text-primary)]">Итого</p>
        <p className="text-price text-[var(--text-primary)]">{totalTenge.toLocaleString()} ₸</p>
      </div>
    </div>
  );
}

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface CheckoutButtonProps {
  deliveryMethod: DeliveryMethod;
  onNavigate?: (page: PageType, data?: { storeId?: string; productId?: string; orderId?: string; trackingId?: string }) => void;
}

export function CheckoutButton({ deliveryMethod, onNavigate }: CheckoutButtonProps) {
  const { items, total, deliveryCost, clearCart } = useCart();
  const { shopConfig } = useShop();
  const { recipient, customer, deliveryAddress, pickupLocation, deliveryTime } = useOrderForm();
  const [isCreating, setIsCreating] = useState(false);

  const totalTenge = Math.floor(total / 100);

  const handleCheckout = async () => {
    // Validation
    if (items.length === 0) {
      alert('Корзина пуста');
      return;
    }

    if (!shopConfig) {
      alert('Ошибка: магазин не определен');
      return;
    }

    // Validate customer phone
    if (!customer.phone || customer.phone.trim() === '') {
      alert('Пожалуйста, введите номер телефона заказчика');
      return;
    }

    // Validate delivery-specific fields
    if (deliveryMethod === 'delivery') {
      if (!recipient.name || recipient.name.trim() === '') {
        alert('Пожалуйста, введите имя получателя');
        return;
      }
      if (!recipient.phone || recipient.phone.trim() === '') {
        alert('Пожалуйста, введите телефон получателя');
        return;
      }
      if (!deliveryAddress.askRecipient && (!deliveryAddress.address || deliveryAddress.address.trim() === '')) {
        alert('Пожалуйста, введите адрес доставки или выберите "Узнать у получателя"');
        return;
      }
    }

    setIsCreating(true);

    try {
      // Build delivery address string
      let fullDeliveryAddress = null;
      if (deliveryMethod === 'delivery') {
        if (deliveryAddress.askRecipient) {
          fullDeliveryAddress = 'Узнать у получателя';
        } else {
          const parts = [deliveryAddress.address];
          if (deliveryAddress.floor) parts.push(`этаж ${deliveryAddress.floor}`);
          if (deliveryAddress.apartment) parts.push(`кв/офис ${deliveryAddress.apartment}`);
          if (deliveryAddress.additionalInfo) parts.push(deliveryAddress.additionalInfo);
          fullDeliveryAddress = parts.join(', ');
        }
      }

      // Build delivery notes
      const deliveryNotes = [
        `Способ доставки: ${deliveryMethod === 'delivery' ? 'Доставка' : 'Самовывоз'}`,
        `Дата: ${deliveryTime.selectedDate === 'today' ? 'Сегодня' : 'Завтра'}`,
        `Время: ${deliveryTime.selectedTimeLabel}`
      ].join('; ');

      // Create order with REAL form data
      const orderData = {
        customerName: customer.phone, // Using customer phone as name for now
        phone: customer.phone,
        customer_email: null,
        delivery_address: fullDeliveryAddress,
        delivery_cost: deliveryCost, // Already in kopecks from CartContext
        delivery_notes: deliveryNotes,
        notes: "Создано через публичный shop интерфейс",
        recipient_name: deliveryMethod === 'delivery' ? recipient.name : null,
        recipient_phone: deliveryMethod === 'delivery' ? recipient.phone : null,
        pickup_address: deliveryMethod === 'pickup' ? pickupLocation.address : null,
        delivery_type: deliveryMethod,
        payment_method: "kaspi", // Kaspi Pay as default payment method
        items: items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          special_requests: item.special_requests || undefined
        })),
        check_availability: false // Don't check availability for now
      };

      const response = await fetch(`${API_BASE_URL}/orders/public/create?shop_id=${shopConfig.id}`, {
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

      // Clear cart after successful order
      clearCart();

      // Navigate to order status page with tracking_id
      if (onNavigate && createdOrder.tracking_id) {
        onNavigate('order-status', {
          orderId: createdOrder.id.toString(),
          trackingId: createdOrder.tracking_id
        });
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
      disabled={isCreating || items.length === 0}
    >
      {isCreating ? 'Создание заказа...' : `Оформить заказ за ${totalTenge.toLocaleString()} ₸`}
    </CvetyButton>
  );
}