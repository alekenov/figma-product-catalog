import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import DeliveryMethodSelector from '../components/cart2/DeliveryMethodSelector';
import DateTimeSelector from '../components/cart2/DateTimeSelector';
import AddressForm from '../components/AddressForm';
import ContactDataForm from '../components/ContactDataForm';
import CartItemsList from '../components/CartItemsList';
import CheckoutButton from '../components/CheckoutButton';
import CvetyCheckbox from '../components/ui/CvetyCheckbox';

/**
 * Cart2Page - страница корзины с дизайном из Figma (node 3:704)
 *
 * Структура: 384px container (16px padding = 352px content area)
 * 6 основных секций с gap 24px
 */
export default function Cart2Page() {
  const navigate = useNavigate();
  const { cartItems, updateQuantity, getCartCount } = useCart();

  // Delivery state
  const [deliveryMethod, setDeliveryMethod] = useState('delivery');
  const [selectedDate, setSelectedDate] = useState('today');
  const [selectedTime, setSelectedTime] = useState('');
  const [addCard, setAddCard] = useState(false);

  // Address state
  const [askRecipient, setAskRecipient] = useState(false);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [floor, setFloor] = useState('');
  const [apartment, setApartment] = useState('');
  const [notes, setNotes] = useState('');

  // Contact state
  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [senderPhone, setSenderPhone] = useState('');

  // Calculate totals
  const itemsTotal = cartItems.reduce(
    (sum, item) => sum + (item.priceValue || 0) * item.quantity,
    0
  );
  const deliveryCost = 1500; // tenge
  const total = itemsTotal + deliveryCost;

  // Handle cart item quantity changes
  const handleQuantityChange = (itemId, newQuantity) => {
    updateQuantity(itemId, newQuantity);
  };

  // Handle checkout
  const handleCheckout = () => {
    console.log('Checkout:', {
      deliveryMethod,
      selectedDate,
      selectedTime,
      addCard,
      askRecipient,
      deliveryAddress,
      floor,
      apartment,
      notes,
      recipientName,
      recipientPhone,
      senderPhone,
      total
    });
    alert('Оформление заказа - функционал в разработке');
  };

  // Format cart items for CartItemsList component
  const formattedCartItems = cartItems.map(item => ({
    id: item.id,
    image: item.image,
    name: item.name,
    size: item.size || 'L',
    price: item.priceValue || 0,
    quantity: item.quantity
  }));

  return (
    <div className="bg-white min-h-screen flex items-center justify-center">
      {/* 384px Container with 16px padding (352px content area) */}
      <div
        className="bg-white flex flex-col"
        style={{
          width: '384px',
          padding: '24px 16px',
          gap: '24px'
        }}
      >
        {/* 1. Delivery Method Selector */}
        <DeliveryMethodSelector
          selectedMethod={deliveryMethod}
          onChange={setDeliveryMethod}
        />

        {/* 2. Date & Time Selector */}
        <DateTimeSelector
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          selectedTime={selectedTime}
          onTimeChange={setSelectedTime}
        />

        {/* 3. Add Card Checkbox */}
        <div
          className="flex items-center px-[16px] py-[16px] rounded-[8px] bg-white"
          style={{ width: '352px', height: '58px' }}
        >
          <div className="flex items-center gap-[12px]">
            {/* Plus Icon */}
            <div className="w-[24px] h-[24px] flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M8 3.33333V12.6667"
                  stroke="var(--text-primary)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
                <path
                  d="M3.33333 8H12.6667"
                  stroke="var(--text-primary)"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </div>
            <CvetyCheckbox
              checked={addCard}
              onChange={setAddCard}
              label="Добавить открытку (бесплатно)"
              size="sm"
            />
          </div>
        </div>

        {/* 4. Address Form */}
        <AddressForm
          askRecipient={askRecipient}
          onAskRecipientChange={setAskRecipient}
          deliveryAddress={deliveryAddress}
          onDeliveryAddressChange={setDeliveryAddress}
          floor={floor}
          onFloorChange={setFloor}
          apartment={apartment}
          onApartmentChange={setApartment}
          notes={notes}
          onNotesChange={setNotes}
        />

        {/* 5. Contact Data Form */}
        <ContactDataForm
          recipientName={recipientName}
          onRecipientNameChange={setRecipientName}
          recipientPhone={recipientPhone}
          onRecipientPhoneChange={setRecipientPhone}
          senderPhone={senderPhone}
          onSenderPhoneChange={setSenderPhone}
        />

        {/* 6. Cart Items List */}
        <CartItemsList
          items={formattedCartItems}
          onQuantityChange={handleQuantityChange}
        />

        {/* 7. Order Summary (simplified from Figma - no card wrapper) */}
        <div style={{ width: '352px' }}>
          <div className="flex flex-col gap-[12px]">
            {/* Товаров на сумму */}
            <div className="flex items-center justify-between" style={{ height: '26px' }}>
              <span className="font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[var(--text-secondary)]">
                Товаров на сумму
              </span>
              <span className="font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[var(--text-primary)]">
                {itemsTotal.toLocaleString('ru-KZ')} ₸
              </span>
            </div>

            {/* Доставка */}
            <div className="flex items-center justify-between" style={{ height: '26px' }}>
              <span className="font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[var(--text-secondary)]">
                Доставка
              </span>
              <span className="font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[var(--text-primary)]">
                {deliveryCost.toLocaleString('ru-KZ')} ₸
              </span>
            </div>

            {/* Divider */}
            <div className="border-t border-[var(--border-default)] my-[1px]" />

            {/* Итого */}
            <div className="flex items-center justify-between" style={{ height: '24px' }}>
              <span className="font-['Open_Sans'] font-normal text-[16px] leading-[24px] text-[var(--text-primary)]">
                Итого
              </span>
              <span className="font-['Open_Sans'] font-semibold text-[16px] leading-[18px] text-[var(--text-primary)]">
                {total.toLocaleString('ru-KZ')} ₸
              </span>
            </div>
          </div>
        </div>

        {/* 8. Checkout Button */}
        <CheckoutButton
          total={total}
          onClick={handleCheckout}
          disabled={cartItems.length === 0}
        />
      </div>
    </div>
  );
}
