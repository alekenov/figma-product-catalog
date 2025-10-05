import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

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

export default function DateTimeSelector({ selectedDate, onDateChange, selectedTime, onTimeChange }) {
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
