import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

export default function InputField({ label, value, onChange, placeholder = '', type = 'text' }) {
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
