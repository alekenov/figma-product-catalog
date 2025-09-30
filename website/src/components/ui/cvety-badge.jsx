import React from 'react';

/**
 * CvetyBadge Component
 *
 * Badge component for status indicators in the Cvety.kz design system.
 *
 * Variants:
 * - default: Default brand color badge
 * - success: Order status, completion states
 * - warning: Alerts, important info
 * - error: Problems, failed states
 * - neutral: General information
 *
 * Sizes:
 * - sm: Small badge (12px text)
 * - default: Default badge (14px text)
 *
 * @example
 * <CvetyBadge variant="success">
 *   Доставлен
 * </CvetyBadge>
 */

export const CvetyBadge = ({
  children,
  variant = 'default',
  size = 'default',
  className = '',
  ...props
}) => {
  const baseStyles = `
    inline-flex items-center justify-center
    font-medium rounded-full
    whitespace-nowrap
  `;

  const variantStyles = {
    default: `
      bg-[var(--brand-primary)] bg-opacity-10
      text-[var(--brand-primary)]
      border border-[var(--brand-primary)]
    `,
    success: `
      bg-[var(--brand-success)] bg-opacity-10
      text-[var(--brand-success)]
      border border-[var(--brand-success)]
    `,
    warning: `
      bg-[var(--brand-warning)] bg-opacity-10
      text-[var(--brand-warning)]
      border border-[var(--brand-warning)]
    `,
    error: `
      bg-[var(--brand-error)] bg-opacity-10
      text-[var(--brand-error)]
      border border-[var(--brand-error)]
    `,
    neutral: `
      bg-[var(--bg-tertiary)]
      text-[var(--text-secondary)]
      border border-[var(--border-default)]
    `,
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    default: 'px-3 py-1 text-sm',
  };

  const combinedClassName = `
    ${baseStyles}
    ${variantStyles[variant]}
    ${sizeStyles[size]}
    ${className}
  `.replace(/\s+/g, ' ').trim();

  return (
    <span className={combinedClassName} {...props}>
      {children}
    </span>
  );
};

export default CvetyBadge;