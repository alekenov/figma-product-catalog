import React from 'react';

/**
 * PriceFormatter Component - Implementation following TDD
 * This implementation was created to satisfy the test specifications
 */
const PriceFormatter = ({
  price,
  variant = 'default',
  color,
  showSign = false,
  currency = '₸',
}) => {
  // Handle undefined price
  if (price === undefined || price === null) {
    return <span className="text-gray-900">—</span>;
  }

  // Format number with space thousands separator
  const formatNumber = (num) => {
    const absNum = Math.abs(num);
    return absNum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  };

  // Format the price value
  const formattedNumber = formatNumber(price);
  const sign = price < 0 ? '-' : (showSign && price > 0 ? '+' : '');

  // Format display text based on currency position
  const displayText = currency === '$'
    ? `${sign}${currency}${formattedNumber}`
    : `${sign}${formattedNumber} ${currency}`;

  // Determine color class
  const getColorClass = () => {
    if (color === 'success') return 'text-green-success';
    if (color === 'error') return 'text-red-500';
    if (price < 0 && !color) return 'text-red-500';
    return 'text-gray-900';
  };

  // Determine size classes based on variant
  const getSizeClasses = () => {
    switch (variant) {
      case 'large':
        return 'text-2xl font-bold';
      case 'small':
        return 'text-sm';
      case 'inline':
        return '';
      default:
        return '';
    }
  };

  // Create ARIA label for accessibility
  const getAriaLabel = () => {
    const absValue = Math.abs(price);
    const prefix = price < 0 ? 'минус ' : '';
    return `${prefix}${absValue} тенге`;
  };

  // Combine all classes
  const className = `${getColorClass()} ${getSizeClasses()}`.trim();

  // Render based on variant
  const Tag = variant === 'inline' ? 'span' : 'div';

  return (
    <Tag
      className={className}
      aria-label={getAriaLabel()}
    >
      {displayText}
    </Tag>
  );
};

export default PriceFormatter;