import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { clientsAPI } from './services/api';
import './App.css';

const CreateOrderCustomer = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedProducts, total } = location.state || {};

  // Redirect if no products selected
  useEffect(() => {
    if (!selectedProducts || Object.keys(selectedProducts).length === 0) {
      navigate('/create-order');
    }
  }, [selectedProducts, navigate]);

  // Sender (заказчик) fields
  const [senderPhone, setSenderPhone] = useState('');
  const [senderName, setSenderName] = useState('');
  const [senderFound, setSenderFound] = useState(false);

  // Recipient (получатель) fields
  const [sameAsCustomer, setSameAsCustomer] = useState(false);
  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');

  // Delivery fields
  const [deliveryDate, setDeliveryDate] = useState('');
  const [deliveryTimeSlot, setDeliveryTimeSlot] = useState('');
  const [deliveryNotes, setDeliveryNotes] = useState('');

  // Time slots
  const timeSlots = [
    '09:00-11:00',
    '11:00-13:00',
    '13:00-15:00',
    '15:00-17:00',
    '17:00-19:00',
    '19:00-21:00'
  ];

  // Search for client by phone
  useEffect(() => {
    const searchClient = async () => {
      if (senderPhone.length >= 10) {
        try {
          const clients = await clientsAPI.getClients({ search: senderPhone, limit: 1 });
          if (clients && clients.length > 0) {
            setSenderName(clients[0].customerName || '');
            setSenderFound(true);
          } else {
            setSenderFound(false);
          }
        } catch (error) {
          console.error('Error searching for client:', error);
          setSenderFound(false);
        }
      } else {
        setSenderFound(false);
      }
    };

    const timeoutId = setTimeout(searchClient, 500);
    return () => clearTimeout(timeoutId);
  }, [senderPhone]);

  // Handle same as customer checkbox
  useEffect(() => {
    if (sameAsCustomer) {
      setRecipientName(senderName);
      setRecipientPhone(senderPhone);
    } else {
      setRecipientName('');
      setRecipientPhone('');
    }
  }, [sameAsCustomer, senderName, senderPhone]);

  const handleBack = () => {
    navigate('/create-order', { state: { selectedProducts, total } });
  };

  const handleNext = () => {
    // Validate required fields
    if (!senderPhone || !senderName || !recipientName || !recipientPhone ||
        !deliveryAddress || !deliveryDate || !deliveryTimeSlot) {
      alert('Пожалуйста, заполните все обязательные поля');
      return;
    }

    const customerData = {
      sender: {
        phone: senderPhone,
        name: senderName
      },
      recipient: {
        name: recipientName,
        phone: recipientPhone
      },
      delivery: {
        address: deliveryAddress,
        date: deliveryDate,
        timeSlot: deliveryTimeSlot,
        notes: deliveryNotes
      }
    };

    navigate('/create-order/review', {
      state: { selectedProducts, total, customerData }
    });
  };

  // Format phone number
  const formatPhoneNumber = (value) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 11) {
      return cleaned;
    }
    return cleaned.slice(0, 11);
  };

  // Get today's date in YYYY-MM-DD format for min date
  const today = new Date().toISOString().split('T')[0];

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
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-primary rounded-full flex items-center justify-center text-white text-[14px] font-bold">2</div>
            <span className="text-[14px] font-['Open_Sans'] text-black">Клиент</span>
          </div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-gray-neutral rounded-full flex items-center justify-center text-gray-disabled text-[14px] font-bold">3</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Проверка</span>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="overflow-y-auto px-4" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {/* Sender Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Заказчик</h2>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Телефон *
            </label>
            <input
              type="tel"
              value={senderPhone}
              onChange={(e) => setSenderPhone(formatPhoneNumber(e.target.value))}
              placeholder="7XXXXXXXXXX"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
            {senderFound && (
              <p className="text-[12px] font-['Open_Sans'] text-green-success mt-1">
                Клиент найден в базе
              </p>
            )}
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Имя *
            </label>
            <input
              type="text"
              value={senderName}
              onChange={(e) => setSenderName(e.target.value)}
              placeholder="Имя заказчика"
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            />
          </div>
        </div>

        {/* Recipient Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Получатель</h2>

          <label className="flex items-center mb-4">
            <input
              type="checkbox"
              checked={sameAsCustomer}
              onChange={(e) => setSameAsCustomer(e.target.checked)}
              className="w-5 h-5 text-purple-primary border-gray-border rounded focus:ring-purple-primary mr-3"
            />
            <span className="text-[16px] font-['Open_Sans']">Заказчик является получателем</span>
          </label>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Имя получателя *
            </label>
            <input
              type="text"
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
              disabled={sameAsCustomer}
              placeholder="Имя получателя"
              className={`w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder ${
                sameAsCustomer ? 'opacity-50' : ''
              }`}
            />
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Телефон получателя *
            </label>
            <input
              type="tel"
              value={recipientPhone}
              onChange={(e) => setRecipientPhone(formatPhoneNumber(e.target.value))}
              disabled={sameAsCustomer}
              placeholder="7XXXXXXXXXX"
              className={`w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder ${
                sameAsCustomer ? 'opacity-50' : ''
              }`}
            />
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Адрес доставки *
            </label>
            <textarea
              value={deliveryAddress}
              onChange={(e) => setDeliveryAddress(e.target.value)}
              placeholder="Улица, дом, квартира"
              rows={3}
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
            />
          </div>
        </div>

        {/* Delivery Section */}
        <div className="mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Доставка</h2>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Дата доставки *
            </label>
            <input
              type="date"
              value={deliveryDate}
              onChange={(e) => setDeliveryDate(e.target.value)}
              min={today}
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans']"
            />
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Время доставки *
            </label>
            <div className="grid grid-cols-2 gap-2">
              {timeSlots.map((slot) => (
                <label key={slot} className="flex items-center">
                  <input
                    type="radio"
                    value={slot}
                    checked={deliveryTimeSlot === slot}
                    onChange={(e) => setDeliveryTimeSlot(e.target.value)}
                    className="w-4 h-4 text-purple-primary border-gray-border focus:ring-purple-primary mr-2"
                  />
                  <span className="text-[14px] font-['Open_Sans']">{slot}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-[14px] font-['Open_Sans'] text-gray-placeholder mb-2">
              Заметки для курьера
            </label>
            <textarea
              value={deliveryNotes}
              onChange={(e) => setDeliveryNotes(e.target.value)}
              placeholder="Дополнительная информация"
              rows={3}
              className="w-full px-4 py-3 bg-gray-input rounded-lg text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
            />
          </div>
        </div>
      </div>

      {/* Bottom Button */}
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-border px-4 py-4">
        <button
          onClick={handleNext}
          className="w-full py-3 bg-purple-primary rounded-lg text-white text-[16px] font-['Open_Sans'] font-semibold"
        >
          Далее
        </button>
      </div>
    </div>
  );
};

export default CreateOrderCustomer;