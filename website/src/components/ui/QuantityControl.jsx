import React from 'react';

/**
 * QuantityControl - Quantity selector from Figma (128x40px)
 *
 * @param {number} quantity - Current quantity
 * @param {function} onDecrease - Callback for minus button
 * @param {function} onIncrease - Callback for plus button
 * @param {number} min - Minimum quantity (default: 0)
 */
export default function QuantityControl({
  quantity = 1,
  onDecrease,
  onIncrease,
  min = 0
}) {
  return (
    <div
      className="bg-neutral-100 rounded-[8px] flex items-center justify-between"
      style={{
        width: '128px',
        height: '40px',
        padding: '0 12px'
      }}
    >
      {/* Minus Button */}
      <button
        onClick={onDecrease}
        disabled={quantity <= min}
        className="flex items-center justify-center"
        style={{
          width: '24px',
          height: '24px'
        }}
        aria-label="Decrease quantity"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path
            d="M2 7H12"
            stroke="var(--text-primary)"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
      </button>

      {/* Quantity Display */}
      <div
        className="font-sans font-semibold text-center"
        style={{
          fontSize: '14px',
          lineHeight: '20px',
          width: '24px',
          color: 'var(--text-primary)'
        }}
      >
        {quantity}
      </div>

      {/* Plus Button */}
      <button
        onClick={onIncrease}
        className="flex items-center justify-center"
        style={{
          width: '24px',
          height: '24px'
        }}
        aria-label="Increase quantity"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 3V13M3 8H13"
            stroke="var(--text-primary)"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
      </button>
    </div>
  );
}
