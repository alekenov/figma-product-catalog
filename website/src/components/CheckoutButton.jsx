import React from 'react';

/**
 * CheckoutButton - Checkout button from Figma (352px width × 56px height)
 *
 * @param {number} total - Total amount in tenge
 * @param {function} onClick - Callback when button is clicked
 * @param {boolean} disabled - Whether button is disabled
 */
export default function CheckoutButton({ total = 0, onClick, disabled = false }) {
  const formatPrice = (amount) => {
    return amount.toLocaleString('ru-KZ');
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="rounded-[12px] flex items-center justify-center"
      style={{
        width: '352px',
        height: '56px',
        backgroundColor: 'var(--brand-primary)'
      }}
    >
      <span
        className="font-sans font-medium"
        style={{
          fontSize: '18px',
          lineHeight: '28px',
          color: 'var(--text-inverse)'
        }}
      >
        Оформить заказ за {formatPrice(total)} ₸
      </span>
    </button>
  );
}