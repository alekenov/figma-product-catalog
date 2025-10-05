import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

export default function TextareaField({ label, value, onChange, placeholder }) {
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
