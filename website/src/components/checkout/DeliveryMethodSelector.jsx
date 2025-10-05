import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

const DELIVERY_OPTIONS = [
  { id: 'delivery', title: 'Доставка', subtitle: 'от 30 мин.' },
  { id: 'pickup', title: 'Самовывоз', subtitle: 'От 30 мин.' }
];

export default function DeliveryMethodSelector({ value, onChange }) {
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
