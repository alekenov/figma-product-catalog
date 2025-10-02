import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { previewOrder, createOrder } from '../services/api';
import { tengeToKopecks } from '../utils/price';
import DeliveryTimeSelector from '../components/DeliveryTimeSelector';
import AddressForm from '../components/AddressForm';
import ContactDataForm from '../components/ContactDataForm';
import CartItemsList from '../components/CartItemsList';
import OrderSummary from '../components/OrderSummary';
import CheckoutButton from '../components/CheckoutButton';
import CvetyCheckbox from '../components/ui/CvetyCheckbox';

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
  const [deliveryMethod, setDeliveryMethod] = useState('delivery'); // 'delivery' or 'pickup'
  const [selectedDate, setSelectedDate] = useState('today'); // 'today', 'tomorrow', or day number
  const [selectedTime, setSelectedTime] = useState(''); // time slot ID
  const [addCard, setAddCard] = useState(false); // greeting card option

  // Address state
  const [askRecipient, setAskRecipient] = useState(false);
  const [floor, setFloor] = useState('');
  const [apartment, setApartment] = useState('');
  const [notes, setNotes] = useState('');

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
        delivery_type: deliveryMethod === 'delivery' ? 'delivery' : 'pickup',
        scheduled_time: `${selectedDate} ${selectedTime}`, // Combine date and time
        delivery_cost: deliveryCostKopecks, // in kopecks
        payment_method: paymentMethod,
        order_comment: addCard ? `${orderComment}\nДобавить открытку` : orderComment,
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

      // Navigate to order status page using tracking_id (no encoding needed)
      // tracking_id is a clean 9-digit number without special characters
      navigate(`/status/${createdOrder.tracking_id}`);

    } catch (error) {
      console.error('Checkout failed:', error);
      alert(`Ошибка при оформлении заказа: ${error.message}`);
    }
  };

  // Handle cart item quantity changes
  const handleQuantityChange = (itemId, newQuantity) => {
    updateQuantity(itemId, newQuantity);
  };

  // Calculate totals
  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.priceValue * item.quantity,
    0
  );
  const delivery = 1500; // tenge
  const total = subtotal + delivery;

  // Format cart items for CartItemsList component
  const formattedCartItems = cartItems.map(item => ({
    id: item.id,
    image: item.image,
    name: item.name,
    size: item.size,
    price: item.priceValue,
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
        {/* Delivery Method & Time Selector */}
        <DeliveryTimeSelector
          deliveryMethod={deliveryMethod}
          onDeliveryMethodChange={setDeliveryMethod}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          selectedTime={selectedTime}
          onTimeChange={setSelectedTime}
          addCard={addCard}
          onAddCardChange={setAddCard}
        />

        {/* Add Card Checkbox */}
        <div style={{ width: '352px' }}>
          <CvetyCheckbox
            checked={addCard}
            onChange={setAddCard}
            label="Добавить открытку (бесплатно)"
            size="sm"
          />
        </div>

        {/* Address Form */}
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

        {/* Contact Data Form */}
        <ContactDataForm
          recipientName={recipientName}
          onRecipientNameChange={setRecipientName}
          recipientPhone={recipientPhone}
          onRecipientPhoneChange={setRecipientPhone}
          senderPhone={senderPhone}
          onSenderPhoneChange={setSenderPhone}
        />

        {/* Cart Items List */}
        <CartItemsList
          items={formattedCartItems}
          onQuantityChange={handleQuantityChange}
        />

        {/* Order Summary */}
        <OrderSummary
          subtotal={subtotal}
          delivery={delivery}
          total={total}
        />

        {/* Checkout Button */}
        <CheckoutButton
          total={total}
          onClick={handleCheckout}
          disabled={cartItems.length === 0}
        />
      </div>
    </div>
  );
}
