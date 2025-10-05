import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

const priceFormatter = new Intl.NumberFormat('ru-KZ');

export default function Summary({ subtotal, delivery, total, deliveryMethod }) {
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
