import React from 'react';

/**
 * CvetyButton Component
 *
 * Primary button component for all interactive actions in the Cvety.kz design system.
 *
 * Variants:
 * - primary: Main actions (Add to Cart, Checkout, Confirm)
 * - secondary: Alternative actions (Edit, View Details)
 * - ghost: Subtle actions (Cancel, Back)
 * - destructive: Delete/remove actions
 *
 * Sizes:
 * - sm: Small button (14px text)
 * - default: Default button (16px text)
 * - lg: Large button (20px text)
 *
 * @example
 * <CvetyButton variant="primary" fullWidth>
 *   В корзину
 * </CvetyButton>
 */

export const CvetyButton = ({
  children,
  variant = 'primary',
  size = 'default',
  fullWidth = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseStyles = `
    inline-flex items-center justify-center
    font-medium rounded-full
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  const variantStyles = {
    primary: `
      bg-[var(--brand-primary)] text-white
      hover:opacity-90 active:opacity-80
      focus:ring-[var(--brand-primary)]
    `,
    secondary: `
      bg-transparent text-[var(--brand-primary)]
      border-2 border-[var(--brand-primary)]
      hover:bg-[var(--brand-primary)] hover:bg-opacity-10
      active:bg-opacity-20
      focus:ring-[var(--brand-primary)]
    `,
    ghost: `
      bg-transparent text-[var(--text-primary)]
      hover:bg-[var(--bg-secondary)]
      active:bg-[var(--bg-tertiary)]
      focus:ring-[var(--text-secondary)]
    `,
    destructive: `
      bg-[var(--brand-error)] text-white
      hover:opacity-90 active:opacity-80
      focus:ring-[var(--brand-error)]
    `,
  };

  const sizeStyles = {
    sm: 'px-4 py-2 text-sm min-h-[32px]',
    default: 'px-6 py-3 text-base min-h-[44px]',
    lg: 'px-8 py-4 text-lg min-h-[52px]',
  };

  const widthStyles = fullWidth ? 'w-full' : '';

  const combinedClassName = `
    ${baseStyles}
    ${variantStyles[variant]}
    ${sizeStyles[size]}
    ${widthStyles}
    ${className}
  `.replace(/\s+/g, ' ').trim();

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={combinedClassName}
      {...props}
    >
      {children}
    </button>
  );
};

export default CvetyButton;