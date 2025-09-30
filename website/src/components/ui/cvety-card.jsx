import React from 'react';

/**
 * CvetyCard Components
 *
 * Card component for content containers in the Cvety.kz design system.
 *
 * Variants:
 * - default: Standard borders for product cards, info sections
 * - elevated: Important content that needs to stand out (with shadow)
 * - outlined: Special emphasis with brand color border
 *
 * @example
 * <CvetyCard variant="elevated">
 *   <CvetyCardHeader>
 *     <CvetyCardTitle>Card Title</CvetyCardTitle>
 *   </CvetyCardHeader>
 *   <CvetyCardContent>
 *     Card content goes here
 *   </CvetyCardContent>
 * </CvetyCard>
 */

export const CvetyCard = ({
  children,
  variant = 'default',
  className = '',
  ...props
}) => {
  const baseStyles = `
    bg-[var(--bg-primary)]
    rounded-lg
    overflow-hidden
  `;

  const variantStyles = {
    default: `
      border border-[var(--border-default)]
    `,
    elevated: `
      shadow-lg
    `,
    outlined: `
      border-2 border-[var(--brand-primary)]
    `,
  };

  const combinedClassName = `
    ${baseStyles}
    ${variantStyles[variant]}
    ${className}
  `.replace(/\s+/g, ' ').trim();

  return (
    <div className={combinedClassName} {...props}>
      {children}
    </div>
  );
};

export const CvetyCardHeader = ({
  children,
  className = '',
  ...props
}) => {
  const headerStyles = `
    px-4 py-3
    border-b border-[var(--border-default)]
  `;

  const combinedClassName = `${headerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  return (
    <div className={combinedClassName} {...props}>
      {children}
    </div>
  );
};

export const CvetyCardTitle = ({
  children,
  className = '',
  ...props
}) => {
  const titleStyles = `
    text-lg font-semibold
    text-[var(--text-primary)]
  `;

  const combinedClassName = `${titleStyles} ${className}`.replace(/\s+/g, ' ').trim();

  return (
    <h3 className={combinedClassName} {...props}>
      {children}
    </h3>
  );
};

export const CvetyCardContent = ({
  children,
  className = '',
  ...props
}) => {
  const contentStyles = `
    px-4 py-3
  `;

  const combinedClassName = `${contentStyles} ${className}`.replace(/\s+/g, ' ').trim();

  return (
    <div className={combinedClassName} {...props}>
      {children}
    </div>
  );
};

export default CvetyCard;