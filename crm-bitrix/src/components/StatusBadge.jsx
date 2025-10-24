import React from 'react';

const StatusBadge = ({ status, label, size = 'md' }) => {
  const getStatusStyles = (status) => {
    const statusMap = {
      new: 'bg-status-new text-white',
      paid: 'bg-blue-500 text-white',
      accepted: 'bg-purple-500 text-white',
      assembled: 'bg-yellow-400 text-black',
      in_delivery: 'bg-green-400 text-white',
      default: 'bg-gray-100 text-gray-800'
    };
    return statusMap[status] || statusMap.default;
  };

  const sizeStyles = {
    sm: 'px-1 py-0.5 text-xs',
    md: 'px-1.5 py-1 text-sm',
    lg: 'px-2 py-1.5 text-base'
  };

  return (
    <div className={`inline-block rounded-full font-['Open_Sans'] font-normal uppercase tracking-wider ${getStatusStyles(status)} ${sizeStyles[size]}`}>
      {label}
    </div>
  );
};

export default StatusBadge;