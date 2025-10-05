import React, { useState } from 'react';
import styles from '../../pages/KorizinaPage.module.css';

export default function GreetingCardSection({ hasCard, cardText, onCardTextChange, onHasCardChange }) {
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
            <div className={styles.cardQuote}>"{cardText}"</div>
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
