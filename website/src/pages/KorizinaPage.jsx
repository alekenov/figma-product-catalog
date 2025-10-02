import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { previewOrder, createOrder } from '../services/api';
import { tengeToKopecks } from '../utils/price';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import styles from './KorizinaPage.module.css';

const priceFormatter = new Intl.NumberFormat('ru-KZ');

const DELIVERY_OPTIONS = [
  { id: 'delivery', title: 'Доставка', subtitle: 'от 30 мин.' },
  { id: 'pickup', title: 'Самовывоз', subtitle: 'От 30 мин.' }
];

const DATE_OPTIONS = [
  { id: 'today', label: 'Сегодня', highlight: true },
  { id: 'tomorrow', label: 'Завтра', highlight: false },
  { id: '9', label: '9', highlight: true }
];

const TIME_OPTIONS = [
  { id: '120-150', label: '120-150 мин', highlight: true },
  { id: '18:00-19:00', label: '18:00-19:00', highlight: false },
  { id: '19:00-20:00', label: '19:00-20:00', highlight: false }
];

function DeliveryMethodSelector({ value, onChange }) {
  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>Способ доставки</h3>
      <div className={styles.deliveryOptions}>
        {DELIVERY_OPTIONS.map((option) => {
          const selected = value === option.id;
          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onChange(option.id)}
              className={`${styles.deliveryOption} ${selected ? styles.deliveryOptionSelected : ''}`}
            >
              <div className={styles.deliveryOptionHeader}>
                <p className={styles.deliveryOptionTitle}>{option.title}</p>
                <span className={`${styles.radioCircle} ${selected ? styles.radioCircleActive : ''}`}>
                  {selected && <span className={styles.radioDot} />}
                </span>
              </div>
              <p className={styles.deliveryOptionSubtitle}>{option.subtitle}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function DateTimeSelector({ selectedDate, onDateChange, selectedTime, onTimeChange }) {
  return (
    <div className={styles.section}>
      <div className={styles.dateTimeHeader}>
        <span className={styles.iconCircle}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M8 14.4C11.5346 14.4 14.4 11.5346 14.4 8C14.4 4.46538 11.5346 1.6 8 1.6C4.46538 1.6 1.6 4.46538 1.6 8C1.6 11.5346 4.46538 14.4 8 14.4Z"
              stroke="#000000"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M8 4.8V8L10 10"
              stroke="#000000"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <h3 className={styles.dateTimeTitle}>Дата и время</h3>
      </div>

      <div className={styles.pillRow}>
        {DATE_OPTIONS.map((option) => {
          const selected = selectedDate === option.id;
          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onDateChange(option.id)}
              className={`${styles.pillButton} ${selected ? styles.pillSelected : ''}`}
            >
              {option.label}
              {option.highlight && <span className={styles.pillDot} />}
            </button>
          );
        })}
      </div>

      <div className={styles.pillRow}>
        {TIME_OPTIONS.map((option) => {
          const selected = selectedTime === option.id;
          return (
            <button
              key={option.id}
              type="button"
              onClick={() => onTimeChange(option.id)}
              className={`${styles.pillButton} ${selected ? styles.pillSelected : ''}`}
            >
              {option.label}
              {option.highlight && <span className={styles.pillDot} />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function GreetingCardSection({ hasCard, cardText, onCardTextChange, onHasCardChange }) {
  const [expanded, setExpanded] = useState(false);
  const [draft, setDraft] = useState(cardText);
  const maxLength = 200;

  const handleOpen = () => {
    setDraft(cardText);
    setExpanded(true);
  };

  const handleCancel = () => {
    if (!hasCard) {
      setDraft('');
      onCardTextChange('');
    }
    setExpanded(false);
  };

  const handleSave = () => {
    const trimmed = draft.trim();
    if (!trimmed || trimmed.length > maxLength) {
      return;
    }
    onCardTextChange(trimmed);
    onHasCardChange(true);
    setExpanded(false);
  };

  const handleRemove = () => {
    onHasCardChange(false);
    onCardTextChange('');
    setDraft('');
    setExpanded(false);
  };

  const disabled = !draft.trim() || draft.trim().length > maxLength;

  if (!expanded) {
    return (
      <div
        className={`${styles.cardContainer} ${styles.cardStatic}`}
        onClick={!hasCard ? handleOpen : undefined}
        role={!hasCard ? 'button' : undefined}
        tabIndex={!hasCard ? 0 : undefined}
        onKeyDown={(event) => {
          if (!hasCard && (event.key === 'Enter' || event.key === ' ')) {
            event.preventDefault();
            handleOpen();
          }
        }}
      >
        {!hasCard && (
          <div className={styles.cardRow}>
            <span className={styles.cardCircle}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M12 8V16M8 12H16" stroke="#8f8f8f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <p className={styles.helperText}>Добавить открытку (бесплатно)</p>
          </div>
        )}

        {hasCard && (
          <div className="">
            <div className={styles.cardRow}>
              <span className={`${styles.cardCircle} ${styles.cardCircleActive}`}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                  <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <p className={styles.helperText} style={{ color: '#000000', fontWeight: 500 }}>
                Открытка добавлена
              </p>
            </div>
            <div className={styles.cardQuote}>“{cardText}”</div>
            <div className={styles.cardActions}>
              <button type="button" className={styles.cardButton} onClick={handleOpen}>
                Изменить
              </button>
              <button type="button" className={styles.cardButton} onClick={handleRemove}>
                Удалить
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={styles.cardContainer}>
      <div className={styles.cardRow}>
        <span className={`${styles.cardCircle} ${styles.cardCircleActive}`}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <p className={styles.helperText} style={{ color: '#000000', fontWeight: 500 }}>
          Текст для открытки
        </p>
      </div>
      <textarea
        className={styles.cardTextarea}
        placeholder="Например: Дорогая мама, поздравляю с днем рождения! Желаю здоровья, счастья и много радостных моментов!"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        maxLength={maxLength + 8}
      />
      <div className={styles.cardCounter}>
        <span>Максимум {maxLength} символов</span>
        <span className={draft.length > maxLength * 0.9 ? styles.warningText : undefined}>
          {draft.length}/{maxLength}
        </span>
      </div>
      <div className={styles.cardActions}>
        <button
          type="button"
          onClick={handleSave}
          disabled={disabled}
          className={styles.cardPrimaryButton}
        >
          {hasCard ? 'Сохранить' : 'Добавить'}
          {!disabled && <span className={styles.cardCheckmark}>✓</span>}
        </button>
        <button type="button" className={styles.cardButton} onClick={handleCancel}>
          Отменить
        </button>
      </div>
    </div>
  );
}

function InputField({ label, value, onChange, placeholder = '', type = 'text' }) {
  return (
    <div className={styles.inputWrapper}>
      <label className={styles.inputLabel}>{label}</label>
      <input
        className={styles.inputField}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
      />
    </div>
  );
}

function TextareaField({ label, value, onChange, placeholder }) {
  return (
    <div className={styles.inputWrapper}>
      <label className={styles.inputLabel}>{label}</label>
      <textarea
        className={`${styles.inputField} ${styles.textareaField}`}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}

function CheckboxField({ label, checked, onChange }) {
  return (
    <label className={styles.checkboxRow}>
      <input
        type="checkbox"
        className={styles.checkboxInput}
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      <span className={styles.checkboxLabel}>{label}</span>
    </label>
  );
}

function CartItems({ items, onQuantityChange }) {
  if (items.length === 0) {
    return <div className={styles.emptyState}>Корзина пуста</div>;
  }

  return (
    <div className={styles.cartList}>
      {items.map((item) => (
        <div key={item.id} className={styles.cartItem}>
          <div className={styles.cartImage}>
            <img src={item.image} alt={item.name} width={56} height={56} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <div className={styles.cartDetails}>
            <div className={styles.cartInfo}>
              <span className={styles.cartName}>{item.name}</span>
              <span className={styles.cartVariant}>{item.size} / {priceFormatter.format(item.price)} ₸</span>
            </div>
            <div className={styles.quantityControl}>
              <button
                type="button"
                onClick={() => onQuantityChange(item.id, Math.max(1, item.quantity - 1))}
                className={styles.quantityButton}
                disabled={item.quantity <= 1}
              >
                −
              </button>
              <span className={styles.quantityValue}>{item.quantity}</span>
              <button
                type="button"
                onClick={() => onQuantityChange(item.id, item.quantity + 1)}
                className={styles.quantityButton}
              >
                +
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function Summary({ subtotal, delivery, total, deliveryMethod }) {
  const deliveryLabel = deliveryMethod === 'pickup' ? 'Самовывоз' : 'Доставка';
  const deliveryValue = deliveryMethod === 'pickup' ? 'Бесплатно' : `${priceFormatter.format(delivery)} ₸`;

  return (
    <div className={styles.summaryList}>
      <div className={styles.summaryRow}>
        <span>Товаров на сумму</span>
        <span>{priceFormatter.format(subtotal)} ₸</span>
      </div>
      <div className={`${styles.summaryRow} ${styles.summaryDivider}`}>
        <span>{deliveryLabel}</span>
        <span>{deliveryValue}</span>
      </div>
      <div className={styles.summaryRow} style={{ fontWeight: 600 }}>
        <span>Итого</span>
        <span>{priceFormatter.format(total)} ₸</span>
      </div>
    </div>
  );
}

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
