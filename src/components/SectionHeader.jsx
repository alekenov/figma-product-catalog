import React from 'react';

const SectionHeader = ({ title, action, className = '' }) => {
  return (
    <div className={`flex items-center justify-between mb-4 ${className}`}>
      <h2 className="text-xl font-['Open_Sans'] text-black leading-relaxed">{title}</h2>
      {action && (
        <div className="flex items-center">
          {action}
        </div>
      )}
    </div>
  );
};

export default SectionHeader;