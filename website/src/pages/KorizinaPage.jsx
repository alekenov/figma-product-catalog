import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { previewOrder, createOrder } from '../services/api';
import { tengeToKopecks } from '../utils/price';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import DeliveryMethodSelector from '../components/checkout/DeliveryMethodSelector';
import DateTimeSelector from '../components/checkout/DateTimeSelector';
import GreetingCardSection from '../components/checkout/GreetingCardSection';
import CartItems from '../components/checkout/CartItems';
import Summary from '../components/checkout/Summary';
import InputField from '../components/ui/InputField';
import TextareaField from '../components/ui/TextareaField';
import CheckboxField from '../components/ui/CheckboxField';
import styles from './KorizinaPage.module.css';

const priceFormatter = new Intl.NumberFormat('ru-KZ');

export default function KorizinaPage() {
  const navigate = useNavigate();
  const { cartItems, updateQuantity, getCartCount, clearCart } = useCart();

  const [deliveryMethod, setDeliveryMethod] = useState('delivery');
  const [selectedDate, setSelectedDate] = useState('today');
  const [selectedTime, setSelectedTime] = useState('120-150');
  const [hasCard, setHasCard] = useState(false);
  const [cardText, setCardText] = useState('');

  const [askRecipient, setAskRecipient] = useState(false);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [floor, setFloor] = useState('');
  const [apartment, setApartment] = useState('');
  const [notes, setNotes] = useState('');

  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [senderPhone, setSenderPhone] = useState('');

  const subtotal = cartItems.reduce((acc, item) => acc + item.priceValue * item.quantity, 0);
  const deliveryCost = deliveryMethod === 'delivery' ? 1500 : 0;
  const total = subtotal + deliveryCost;

  const formattedCartItems = cartItems.map((item) => ({
    id: item.id,
    image: item.image,
    name: item.name,
    size: item.size,
    price: item.priceValue,
    quantity: item.quantity
  }));

  const orderComment = useMemo(() => {
    const messages = [];
    if (hasCard && cardText.trim()) {
      messages.push(`Открытка: ${cardText.trim()}`);
    }
    if (notes.trim()) {
      messages.push(`Примечания: ${notes.trim()}`);
    }
    return messages.join('\n');
  }, [cardText, hasCard, notes]);

  const handleCheckout = async () => {
    try {
      const previewItems = cartItems.map((item) => ({
        product_id: item.productId,
        quantity: item.quantity
      }));

      const previewResult = await previewOrder(previewItems);
      if (!previewResult.available) {
        const warningsText = previewResult.warnings.join(', ');
        alert(`Извините, некоторые товары недоступны: ${warningsText}`);
        return;
      }

      const itemsTotalKopecks = tengeToKopecks(subtotal);
      const deliveryCostKopecks = tengeToKopecks(deliveryCost);
      const totalKopecks = itemsTotalKopecks + deliveryCostKopecks;
      const bonusPointsKopecks = Math.floor(totalKopecks * 0.02);

      const orderPayload = {
        customerName: recipientName || 'Клиент',
        phone: senderPhone || '+77777777777',
        recipient_name: recipientName,
        recipient_phone: recipientPhone,
        sender_phone: senderPhone,
        delivery_address: deliveryAddress,
        pickup_address: 'г. Астана, пр. Мангилик Ел 55',
        delivery_type: deliveryMethod === 'delivery' ? 'delivery' : 'pickup',
        scheduled_time: `${selectedDate} ${selectedTime}`,
        delivery_cost: deliveryCostKopecks,
        payment_method: '',
        order_comment: orderComment,
        bonus_points: bonusPointsKopecks,
        items: cartItems.map((item) => ({
          product_id: item.productId,
          quantity: item.quantity,
          special_requests: null
        })),
        check_availability: true
      };

      const createdOrder = await createOrder(orderPayload);

      clearCart();
      navigate(`/status/${createdOrder.tracking_id}`);
    } catch (error) {
      console.error('Checkout failed:', error);
      alert(`Ошибка при оформлении заказа: ${error.message}`);
    }
  };

  return (
    <div className={styles.korizinaPage}>
      <div className={styles.container}>
        <Header cartCount={getCartCount()} />

        <main className={styles.content}>
          <DeliveryMethodSelector value={deliveryMethod} onChange={setDeliveryMethod} />

          <DateTimeSelector
            selectedDate={selectedDate}
            onDateChange={setSelectedDate}
            selectedTime={selectedTime}
            onTimeChange={setSelectedTime}
          />

          <GreetingCardSection
            hasCard={hasCard}
            cardText={cardText}
            onCardTextChange={setCardText}
            onHasCardChange={setHasCard}
          />

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Адрес доставки</h3>
            <div className={styles.formGroup}>
              <CheckboxField
                label="Узнать у получателя"
                checked={askRecipient}
                onChange={setAskRecipient}
              />
              <InputField
                label="Адрес доставки"
                value={deliveryAddress}
                onChange={setDeliveryAddress}
                placeholder="Введите адрес доставки"
              />
              <div className={styles.formRow}>
                <InputField
                  label="Этаж"
                  value={floor}
                  onChange={setFloor}
                  placeholder="Этаж"
                />
                <InputField
                  label="Кв/Офис"
                  value={apartment}
                  onChange={setApartment}
                  placeholder="№ квартиры или офиса"
                />
              </div>
              <TextareaField
                label="Примечания"
                value={notes}
                onChange={setNotes}
                placeholder="Домофон, особые указания"
              />
            </div>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Контактные данные</h3>
            <div className={styles.formGroup}>
              <InputField
                label="Имя получателя"
                value={recipientName}
                onChange={setRecipientName}
                placeholder="Имя получателя"
              />
              <InputField
                label="Телефон получателя"
                value={recipientPhone}
                onChange={setRecipientPhone}
                placeholder="Телефон"
                type="tel"
              />
              <InputField
                label="Ваш телефон"
                value={senderPhone}
                onChange={setSenderPhone}
                placeholder="Номер заказчика"
                type="tel"
              />
            </div>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Ваш заказ</h3>
            <CartItems items={formattedCartItems} onQuantityChange={updateQuantity} />
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Итого</h3>
            <Summary
              subtotal={subtotal}
              delivery={deliveryCost}
              total={total}
              deliveryMethod={deliveryMethod}
            />
          </div>

          <button
            type="button"
            className={styles.checkoutButton}
            onClick={handleCheckout}
            disabled={cartItems.length === 0}
          >
            Оформить заказ за {priceFormatter.format(total)} ₸
          </button>
        </main>

        <Footer />
      </div>
    </div>
  );
}
