import React from 'react';

/**
 * Status Badge Component
 * Displays order/product status with color-coded backgrounds
 *
 * @param {string} status - Status key (new, paid, accepted, assembled, in_delivery)
 * @param {string} label - Display label text
 * @param {string} size - Badge size: sm, md (default), lg
 */
const StatusBadge = ({ status, label, size = 'md' }) => {
  const getStatusStyles = (status) => {
    const statusMap = {
      new: 'bg-status-new text-white',
      paid: 'bg-status-blue text-white',
      accepted: 'bg-status-pink text-white',
      assembled: 'bg-status-assembled text-white',
      in_delivery: 'bg-status-green text-white',
      default: 'bg-gray-input text-gray-disabled'
    };
    return statusMap[status] || statusMap.default;
  };

  const sizeStyles = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-1.5 py-0.75 text-xs',
    lg: 'px-2 py-1.5 text-base'
  };

  return (
    <div className={`inline-block rounded-full font-sans font-normal uppercase tracking-[1.2px] ${getStatusStyles(status)} ${sizeStyles[size]}`}>
      {label}
    </div>
  );
};

export default StatusBadge;