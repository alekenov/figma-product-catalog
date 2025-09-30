import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { previewOrder, createOrder } from '../services/api';
import { tengeToKopecks } from '../utils/price';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import CartItemCard from '../components/CartItemCard';
import OrderSummary from '../components/OrderSummary';
import RecipientForm from '../components/RecipientForm';
import SenderForm from '../components/SenderForm';
import DeliveryTimeSelector from '../components/DeliveryTimeSelector';
import PaymentMethodSelector from '../components/PaymentMethodSelector';
import CheckoutButton from '../components/CheckoutButton';
import CvetyInput from '../components/ui/cvety-input';
import CvetyCheckbox from '../components/ui/CvetyCheckbox';
import { CvetyCard, CvetyCardContent, CvetyCardHeader, CvetyCardTitle } from '../components/ui/cvety-card';

// Mock data для товаров в корзине
const mockCartItems = [
  {
    id: 1,
    image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__',
    name: 'Комбобукет',
    size: 'L',
    price: '6 900 ₸',
    priceValue: 6900,
    quantity: 1
  },
  {
    id: 2,
    image: 'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__',
    name: 'Букет средний',
    size: '15 шт',
    price: '12 500 ₸',
    priceValue: 12500,
    quantity: 2
  },
  {
    id: 3,
    image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__',
    name: 'Букет средний (пожелание белые цветы)',
    size: '1 уп',
    price: '12 500 ₸',
    priceValue: 12500,
    quantity: 1
  }
];

export default function CartPage() {
  const navigate = useNavigate();
  const { cartItems, updateQuantity, getCartCount, clearCart } = useCart();

  // Order state
  const [usePromo, setUsePromo] = useState(false);
  const [orderComment, setOrderComment] = useState('');

  // Recipient state
  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [isSelfRecipient, setIsSelfRecipient] = useState(false);
  const [useStoreAddress, setUseStoreAddress] = useState(false);

  // Delivery state
  const [deliveryType, setDeliveryType] = useState('express');
  const [scheduledTime, setScheduledTime] = useState('');

  // Sender state
  const [senderPhone, setSenderPhone] = useState('');

  // Payment state
  const [paymentMethod, setPaymentMethod] = useState('');
  const [addComment, setAddComment] = useState(false);

  // Cart operations
  const handleQuantityIncrease = (itemId) => {
    const item = cartItems.find(item => item.id === itemId);
    if (item) {
      updateQuantity(itemId, item.quantity + 1);
    }
  };

  const handleQuantityDecrease = (itemId) => {
    const item = cartItems.find(item => item.id === itemId);
    if (item && item.quantity > 1) {
      updateQuantity(itemId, item.quantity - 1);
    }
  };

  // Calculate totals (in tenge for display)
  const itemsTotal = cartItems.reduce(
    (sum, item) => sum + item.priceValue * item.quantity,
    0
  );
  const deliveryCost = 1500; // tenge
  const promoDiscount = 360; // tenge

  const handleCheckout = async () => {
    try {
      // Step 1: Preview order to validate inventory
      const previewItems = cartItems.map(item => ({
        product_id: item.productId,
        quantity: item.quantity
      }));

      const previewResult = await previewOrder(previewItems);

      if (!previewResult.available) {
        // Show error message about unavailable items
        const warningsText = previewResult.warnings.join(', ');
        alert(`Извините, некоторые товары недоступны: ${warningsText}`);
        return;
      }

      // Step 2: Convert all monetary values to kopecks for backend
      const itemsTotalKopecks = tengeToKopecks(itemsTotal);
      const deliveryCostKopecks = tengeToKopecks(deliveryCost);
      const promoDiscountKopecks = tengeToKopecks(promoDiscount);

      // Calculate bonus points: 2% of total in kopecks
      const totalAfterPromoKopecks = itemsTotalKopecks + deliveryCostKopecks - (usePromo ? promoDiscountKopecks : 0);
      const bonusPointsKopecks = Math.floor(totalAfterPromoKopecks * 0.02);

      // Step 3: Create order with full checkout data (all values in kopecks)
      const orderPayload = {
        customerName: recipientName || 'Клиент',
        phone: senderPhone || '+77777777777',
        recipient_name: recipientName,
        recipient_phone: recipientPhone,
        sender_phone: senderPhone,
        delivery_address: deliveryAddress,
        pickup_address: 'г. Астана, пр. Мангилик Ел 55',
        delivery_type: deliveryType,
        scheduled_time: scheduledTime,
        delivery_cost: deliveryCostKopecks, // in kopecks
        payment_method: paymentMethod,
        order_comment: orderComment,
        bonus_points: bonusPointsKopecks, // in kopecks
        items: cartItems.map(item => ({
          product_id: item.productId,
          quantity: item.quantity,
          special_requests: null
        })),
        check_availability: true
      };

      const createdOrder = await createOrder(orderPayload);

      // Clear cart
      clearCart();

      // Navigate to order status page with URL-encoded order number
      // Order numbers contain "#" which must be encoded for URL routing
      const encodedOrderNumber = encodeURIComponent(createdOrder.orderNumber);
      navigate(`/status/${encodedOrderNumber}`);

    } catch (error) {
      console.error('Checkout failed:', error);
      alert(`Ошибка при оформлении заказа: ${error.message}`);
    }
  };

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      <Header cartCount={getCartCount()} />

      <main className="flex-1 px-4 py-6 space-y-6">
          {/* Page Title */}
          <h1 className="font-sans font-bold text-h2 text-text-black">
            В корзине
          </h1>

          {/* Store Info */}
          <CvetyCard>
            <CvetyCardHeader>
              <CvetyCardTitle className="!text-body-1 !font-semibold text-text-black">
                Магазин Combo.kz
              </CvetyCardTitle>
            </CvetyCardHeader>
            <CvetyCardContent className="space-y-4">
              <p className="font-sans font-normal text-field-title text-text-grey-dark">
                Астана пр. Мангилик Ел 55 • 1 500 ₸
              </p>

              {/* Delivery to Store Address Checkbox */}
              <CvetyCheckbox
                checked={useStoreAddress}
                onChange={setUseStoreAddress}
                label="Доставить по адресу этого магазина"
                size="sm"
              />
            </CvetyCardContent>
          </CvetyCard>

          {/* Cart Items */}
          <div className="space-y-4">
            {cartItems.map(item => (
              <CartItemCard
                key={item.id}
                image={item.image}
                name={item.name}
                size={item.size}
                price={item.price}
                quantity={item.quantity}
                onIncrease={() => handleQuantityIncrease(item.id)}
                onDecrease={() => handleQuantityDecrease(item.id)}
              />
            ))}
          </div>

          {/* Order Comment */}
          <CvetyInput
            as="textarea"
            label="Комментарий к заказу"
            value={orderComment}
            onChange={(e) => setOrderComment(e.target.value)}
            placeholder="Ваши пожелания к заказу (необязательно)"
            rows={3}
          />

          {/* Order Summary */}
          <OrderSummary
            itemsTotal={itemsTotal}
            deliveryCost={deliveryCost}
            promoDiscount={promoDiscount}
            usePromo={usePromo}
            onPromoToggle={() => setUsePromo(!usePromo)}
          />

          {/* Recipient Form */}
          <RecipientForm
            recipientName={recipientName}
            recipientPhone={recipientPhone}
            deliveryAddress={deliveryAddress}
            isSelfRecipient={isSelfRecipient}
            onRecipientNameChange={setRecipientName}
            onRecipientPhoneChange={setRecipientPhone}
            onDeliveryAddressChange={setDeliveryAddress}
            onSelfRecipientToggle={setIsSelfRecipient}
          />

          {/* Delivery Time Selector */}
          <DeliveryTimeSelector
            deliveryType={deliveryType}
            scheduledTime={scheduledTime}
            onDeliveryTypeChange={setDeliveryType}
            onScheduledTimeChange={setScheduledTime}
          />

          {/* Sender Form */}
          <SenderForm
            senderPhone={senderPhone}
            onSenderPhoneChange={setSenderPhone}
          />

          {/* Payment Method Selector */}
          <PaymentMethodSelector
            selectedMethod={paymentMethod}
            onMethodSelect={setPaymentMethod}
          />

          {/* Add Comment Checkbox */}
          <CvetyCheckbox
            checked={addComment}
            onChange={setAddComment}
            label="Добавить комментарий к заказу"
            size="sm"
          />

          {/* Checkout Button */}
          <CheckoutButton
            deliveryTime={deliveryType === 'express' ? '35 мин' : scheduledTime || 'Завтра к 12:00'}
            total={itemsTotal + deliveryCost - (usePromo ? promoDiscount : 0)}
            onClick={handleCheckout}
            disabled={cartItems.length === 0}
          />
        </main>

      <Footer />
    </div>
  );
}
