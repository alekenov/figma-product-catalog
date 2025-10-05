import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

const priceFormatter = new Intl.NumberFormat('ru-KZ');

export default function CartItems({ items, onQuantityChange }) {
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
