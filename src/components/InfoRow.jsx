import React from 'react';

const InfoRow = ({ label, value, children, className = '' }) => {
  return (
    <div className={`${className}`}>
      <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">{label}</div>
      <div className="text-base font-['Open_Sans'] text-black">
        {children || value}
      </div>
    </div>
  );
};

export default InfoRow;