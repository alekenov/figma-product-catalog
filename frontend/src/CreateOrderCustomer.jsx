import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ordersAPI } from './services/api';
import { useToast } from './components/ToastProvider';
import './App.css';

const CreateOrderCustomer = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError } = useToast();
  const { selectedProducts, total, delivery } = location.state || {};

  // Redirect if no products selected
  useEffect(() => {
    if (!selectedProducts || Object.keys(selectedProducts).length === 0) {
      navigate('/create-order');
    }
  }, [selectedProducts, navigate]);

  // Заказчик (только телефон для связи)
  const [senderPhone, setSenderPhone] = useState('');

  // Получатель
  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');

  // Текст открытки
  const [cardText, setCardText] = useState('');

  // Адрес доставки (разбит на 4 поля)
  const [streetAddress, setStreetAddress] = useState('');
  const [floor, setFloor] = useState('');
  const [apartment, setApartment] = useState('');
  const [confirmAddressWithRecipient, setConfirmAddressWithRecipient] = useState(false);

  // Комментарий (скрыт по умолчанию)
  const [showCommentField, setShowCommentField] = useState(false);
  const [orderComment, setOrderComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleBack = () => {
    navigate('/create-order', { state: { selectedProducts, total } });
  };

  // Format phone with +7 prefix
  const formatPhoneWithPrefix = (value) => {
    // Remove all non-digits
    const cleaned = value.replace(/\D/g, '');

    if (cleaned.length === 0) {
      return '';
    }

    // If starts with 8, replace with 7
    let formatted = cleaned;
    if (formatted.startsWith('8')) {
      formatted = '7' + formatted.slice(1);
    }

    // If 10 digits, add country code 7 in front
    if (formatted.length === 10) {
      formatted = '7' + formatted;
    }

    // Limit to 11 digits (7 + 10)
    if (formatted.length > 11) {
      formatted = formatted.slice(0, 11);
    }

    // Add + prefix
    return '+' + formatted;
  };

  const handlePhoneChange = (setter) => (e) => {
    const formatted = formatPhoneWithPrefix(e.target.value);
    setter(formatted);
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!senderPhone || !recipientName || !recipientPhone || !streetAddress || !floor || !apartment) {
      showError('Пожалуйста, заполните все обязательные поля');
      return;
    }

    // Validate phone format (+7XXXXXXXXXX = 12 chars)
    if (senderPhone.length !== 12 || recipientPhone.length !== 12) {
      showError('Неверный формат телефона. Ожидается: +7XXXXXXXXXX');
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare order data
      const orderItems = Object.values(selectedProducts).map(item => ({
        product_id: item.product.id,
        quantity: item.quantity,
        special_requests: null
      }));

      // Format delivery datetime from step 1
      const [startTime] = delivery.time.split('-');
      const deliveryDateTime = new Date(`${delivery.date}T${startTime}:00`);

      // Combine address parts
      const fullAddress = `${streetAddress}, ${floor} этаж, ${apartment}${confirmAddressWithRecipient ? ' (уточнить у получателя)' : ''}`;

      // Combine notes with recipient info, card text, and comment
      const notesLines = [
        cardText ? `Текст открытки: ${cardText}` : '',
        `Получатель: ${recipientName}, тел: ${recipientPhone}`,
        delivery.confirmTimeWithRecipient ? 'Время доставки: уточнить у получателя' : '',
        orderComment ? `Комментарий: ${orderComment}` : ''
      ].filter(Boolean);

      const orderData = {
        // Customer info (sender phone only)
        customerName: recipientName, // Use recipient name as primary
        phone: senderPhone,
        customer_email: null,

        // Delivery info
        delivery_address: fullAddress,
        delivery_date: deliveryDateTime.toISOString(),
        delivery_notes: '',
        delivery_cost: 0,

        // Combined notes
        notes: notesLines.join('\n'),

        // Items
        items: orderItems,

        // Disable availability check for now
        check_availability: false
      };

      // Create order with items
      const response = await ordersAPI.createOrderWithItems(orderData);

      showSuccess(`Заказ №${response.orderNumber || response.id} успешно создан`);

      // Navigate to order details
      navigate(`/orders/${response.id}`);
    } catch (error) {
      console.error('Error creating order:', error);
      showError('Ошибка при создании заказа');
    } finally {
      setIsSubmitting(false);
    }
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

      {/* Step indicator (2 steps) */}
      <div className="px-4 mb-4">
        <div className="flex items-center justify-between max-w-[200px]">
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-green-success rounded-full flex items-center justify-center text-white text-[14px] font-bold">✓</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Товары</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-primary rounded-full flex items-center justify-center text-white text-[14px] font-bold">2</div>
            <span className="text-[14px] font-['Open_Sans'] text-black">Клиент</span>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="overflow-y-auto px-4 pb-24" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {/* Получатель Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Получатель</h2>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Имя *
            </label>
            <input
              type="text"
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
              placeholder="Имя получателя"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Телефон *
            </label>
            <input
              type="tel"
              value={recipientPhone}
              onChange={handlePhoneChange(setRecipientPhone)}
              placeholder="+7 (___) ___-__-__"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
          </div>
        </div>

        {/* Текст открытки Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Текст открытки</h2>

          <div className="mb-2">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Что написать в открытке?
            </label>
            <textarea
              value={cardText}
              onChange={(e) => setCardText(e.target.value)}
              placeholder="Например: С днем рождения! Желаю счастья и здоровья!"
              rows={3}
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
            />
          </div>
        </div>

        {/* Адрес доставки Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Адрес доставки</h2>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Улица, дом *
            </label>
            <input
              type="text"
              value={streetAddress}
              onChange={(e) => setStreetAddress(e.target.value)}
              placeholder="ул. Абая 150"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
          </div>

          <div className="mb-4 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
                Этаж *
              </label>
              <input
                type="text"
                value={floor}
                onChange={(e) => setFloor(e.target.value)}
                placeholder="5"
                className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
              />
            </div>
            <div>
              <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
                Кв/Офис *
              </label>
              <input
                type="text"
                value={apartment}
                onChange={(e) => setApartment(e.target.value)}
                placeholder="кв. 25"
                className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={confirmAddressWithRecipient}
              onChange={(e) => setConfirmAddressWithRecipient(e.target.checked)}
              className="w-5 h-5 text-purple-primary border-gray-border rounded focus:ring-purple-primary"
            />
            <span className="text-[14px] font-['Open_Sans']">Уточнить адрес у получателя</span>
          </label>
        </div>

        {/* Заказчик (для связи) Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Заказчик (для связи)</h2>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Телефон *
            </label>
            <input
              type="tel"
              value={senderPhone}
              onChange={handlePhoneChange(setSenderPhone)}
              placeholder="+7 (___) ___-__-__"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
          </div>
        </div>

        {/* Optional Comment Field */}
        {!showCommentField ? (
          <button
            onClick={() => setShowCommentField(true)}
            className="flex items-center gap-2 text-purple-primary text-[16px] font-['Open_Sans'] mb-6"
          >
            <span className="text-[20px] leading-none">+</span>
            <span>Добавить комментарий к заказу</span>
          </button>
        ) : (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder">
                Комментарий к заказу
              </label>
              <button
                onClick={() => {
                  setShowCommentField(false);
                  setOrderComment('');
                }}
                className="text-[14px] text-gray-placeholder"
              >
                Убрать
              </button>
            </div>
            <textarea
              value={orderComment}
              onChange={(e) => setOrderComment(e.target.value)}
              placeholder="Дополнительная информация"
              rows={3}
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
            />
          </div>
        )}
      </div>

      {/* Bottom Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-border" style={{ maxWidth: '320px', margin: '0 auto' }}>
        <div className="px-4 py-4">
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className={`w-full py-3 rounded-lg text-white text-[16px] font-['Open_Sans'] font-semibold ${
              isSubmitting
                ? 'bg-gray-disabled opacity-50 cursor-not-allowed'
                : 'bg-purple-primary'
            }`}
          >
            {isSubmitting ? 'Создание...' : 'Создать заказ'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateOrderCustomer;
