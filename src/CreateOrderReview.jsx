import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ordersAPI } from './services/api';
import { useToast } from './components/ToastProvider';
import './App.css';

const CreateOrderReview = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError } = useToast();
  const { selectedProducts, total, customerData } = location.state || {};

  const [giftCardText, setGiftCardText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if no data
  useEffect(() => {
    if (!selectedProducts || !customerData) {
      navigate('/create-order');
    }
  }, [selectedProducts, customerData, navigate]);

  const handleBack = () => {
    navigate('/create-order/customer', { state: { selectedProducts, total } });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    try {
      // Prepare order data
      const orderItems = Object.values(selectedProducts).map(item => ({
        product_id: item.product.id,
        quantity: item.quantity,
        special_requests: null
      }));

      // Format delivery datetime properly
      const [startTime] = customerData.delivery.timeSlot.split('-');
      const deliveryDateTime = new Date(`${customerData.delivery.date}T${startTime}:00`);

      // Combine recipient info with notes since backend doesn't have recipient fields
      const combinedNotes = `${giftCardText ? `Текст открытки: ${giftCardText}\n` : ''}`
        + `Получатель: ${customerData.recipient.name}, тел: ${customerData.recipient.phone}`;

      const orderData = {
        // Customer info (sender)
        customerName: customerData.sender.name,
        phone: customerData.sender.phone,
        customer_email: null,

        // Delivery info
        delivery_address: customerData.delivery.address,
        delivery_date: deliveryDateTime.toISOString(),
        delivery_notes: customerData.delivery.notes,
        delivery_cost: 0,

        // Combined notes with recipient info and gift card
        notes: combinedNotes,

        // Items
        items: orderItems,

        // Disable availability check for now
        check_availability: false
      };

      // Create order with items
      const response = await ordersAPI.createOrderWithItems(orderData);

      showSuccess(`Заказ №${response.orderNumber || response.id} успешно создан`);

      // Navigate to order details
      navigate(`/order/${response.id}`);
    } catch (error) {
      console.error('Error creating order:', error);
      showError('Ошибка при создании заказа');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!selectedProducts || !customerData) {
    return null;
  }

  // Format delivery date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center px-4 pt-6 pb-4">
        <button onClick={handleBack} className="p-2 -ml-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <h1 className="text-[24px] font-['Open_Sans'] font-normal ml-2">Новый заказ</h1>
      </div>

      {/* Step indicator */}
      <div className="px-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-green-success rounded-full flex items-center justify-center text-white text-[14px] font-bold">✓</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Товары</span>
          </div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-green-success rounded-full flex items-center justify-center text-white text-[14px] font-bold">✓</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Клиент</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-primary rounded-full flex items-center justify-center text-white text-[14px] font-bold">3</div>
            <span className="text-[14px] font-['Open_Sans'] text-black">Проверка</span>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="overflow-y-auto px-4" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {/* Order Summary */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Состав заказа</h2>

          <div className="bg-gray-input rounded-lg p-4">
            {Object.values(selectedProducts).map((item, index) => (
              <div key={item.product.id} className={`flex justify-between items-center ${index > 0 ? 'mt-3 pt-3 border-t border-gray-border' : ''}`}>
                <div className="flex-1">
                  <p className="text-[16px] font-['Open_Sans'] text-black">{item.product.name}</p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    {item.quantity} шт × {item.product.price.toLocaleString()} ₸
                  </p>
                </div>
                <p className="text-[16px] font-['Open_Sans'] font-semibold">
                  {(item.product.price * item.quantity).toLocaleString()} ₸
                </p>
              </div>
            ))}

            <div className="mt-4 pt-4 border-t border-gray-border flex justify-between items-center">
              <span className="text-[18px] font-['Open_Sans'] font-semibold">Итого:</span>
              <span className="text-[20px] font-['Open_Sans'] font-bold text-purple-primary">
                {total.toLocaleString()} ₸
              </span>
            </div>
          </div>
        </div>

        {/* Customer Info */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Заказчик</h2>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="mb-2">
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Имя</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.sender.name}</p>
            </div>
            <div>
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Телефон</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.sender.phone}</p>
            </div>
          </div>
        </div>

        {/* Recipient Info */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Получатель</h2>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="mb-2">
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Имя</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.recipient.name}</p>
            </div>
            <div className="mb-2">
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Телефон</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.recipient.phone}</p>
            </div>
            <div>
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Адрес</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.delivery.address}</p>
            </div>
          </div>
        </div>

        {/* Delivery Info */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Доставка</h2>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="mb-2">
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Дата</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{formatDate(customerData.delivery.date)}</p>
            </div>
            <div className="mb-2">
              <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Время</p>
              <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.delivery.timeSlot}</p>
            </div>
            {customerData.delivery.notes && (
              <div>
                <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Заметки курьеру</p>
                <p className="text-[16px] font-['Open_Sans'] text-black">{customerData.delivery.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Gift Card */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Открытка</h2>

          <textarea
            value={giftCardText}
            onChange={(e) => setGiftCardText(e.target.value)}
            placeholder="Текст поздравления (необязательно)"
            rows={4}
            className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
          />
        </div>
      </div>

      {/* Bottom Button */}
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-border px-4 py-4">
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className={`w-full py-3 rounded-lg text-white text-[16px] font-['Open_Sans'] font-semibold ${
            isSubmitting
              ? 'bg-gray-disabled opacity-50 cursor-not-allowed'
              : 'bg-purple-primary'
          }`}
        >
          {isSubmitting ? 'Создание заказа...' : 'Создать заказ'}
        </button>
      </div>
    </div>
  );
};

export default CreateOrderReview;