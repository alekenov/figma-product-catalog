import React from 'react';

/**
 * CvetyQuantityControl Component
 *
 * Quantity control component for product quantity selection in the Cvety.kz design system.
 *
 * @example
 * <CvetyQuantityControl
 *   value={quantity}
 *   onDecrease={() => setQuantity(q => Math.max(1, q - 1))}
 *   onIncrease={() => setQuantity(q => q + 1)}
 * />
 */

export const CvetyQuantityControl = ({
  value = 1,
  min = 1,
  max = 99,
  onDecrease,
  onIncrease,
  disabled = false,
  className = '',
  ...props
}) => {
  const containerStyles = `
    inline-flex items-center
    border border-[var(--border-default)]
    rounded-lg
    overflow-hidden
  `;

  const buttonStyles = `
    w-10 h-10
    flex items-center justify-center
    bg-[var(--bg-primary)]
    text-[var(--text-primary)]
    transition-colors duration-200
    hover:bg-[var(--bg-secondary)]
    active:bg-[var(--bg-tertiary)]
    disabled:opacity-50 disabled:cursor-not-allowed
    focus:outline-none focus:ring-2 focus:ring-inset focus:ring-[var(--brand-primary)]
  `;

  const valueStyles = `
    w-12
    text-center
    text-base font-medium
    text-[var(--text-primary)]
    bg-[var(--bg-primary)]
    border-x border-[var(--border-default)]
  `;

  const combinedClassName = `${containerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  const handleDecrease = () => {
    if (!disabled && value > min && onDecrease) {
      onDecrease();
    }
  };

  const handleIncrease = () => {
    if (!disabled && value < max && onIncrease) {
      onIncrease();
    }
  };

  return (
    <div className={combinedClassName} {...props}>
      <button
        type="button"
        onClick={handleDecrease}
        disabled={disabled || value <= min}
        className={buttonStyles}
        aria-label="Уменьшить количество"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M3.33325 8H12.6666"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      <div className={valueStyles}>
        {value}
      </div>
      <button
        type="button"
        onClick={handleIncrease}
        disabled={disabled || value >= max}
        className={buttonStyles}
        aria-label="Увеличить количество"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M8 3.33337V12.6667M3.33325 8H12.6666"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  );
};

export default CvetyQuantityControl;