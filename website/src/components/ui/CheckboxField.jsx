import React from 'react';
import styles from '../../pages/KorizinaPage.module.css';

export default function CheckboxField({ label, checked, onChange }) {
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
