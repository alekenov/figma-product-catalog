import React from 'react';

/**
 * DiscountBadge component
 * Displays a discount percentage badge
 *
 * @param {number} discount - Discount percentage (0-100)
 * @param {string} size - Size variant ('sm' | 'md' | 'lg')
 */
const DiscountBadge = ({ discount, size = 'md' }) => {
  if (!discount || discount <= 0) return null;

  const sizeStyles = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  return (
    <div
      className={`
        absolute top-2 right-2
        bg-red-500 text-white
        font-['Open_Sans'] font-bold
        rounded
        ${sizeStyles[size]}
      `}
    >
      -{discount}%
    </div>
  );
};

export default DiscountBadge;
