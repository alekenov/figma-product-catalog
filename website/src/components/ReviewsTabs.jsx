import React, { useState } from 'react';

/**
 * ReviewsTabs - табы для отзывов (о товаре / о компании)
 *
 * @param {number} productReviewsCount - Количество отзывов о товаре
 * @param {number} companyReviewsCount - Количество отзывов о компании
 * @param {function} onTabChange - Колбэк при смене таба
 */
export default function ReviewsTabs({ productReviewsCount, companyReviewsCount, onTabChange }) {
  const [activeTab, setActiveTab] = useState('product');

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    onTabChange?.(tab);
  };

  return (
    <div className="flex border-b-2 border-[var(--bg-tertiary)]">
      {/* Product Reviews Tab */}
      <button
        onClick={() => handleTabChange('product')}
        className={`p-[10px] font-sans font-semibold text-[14px] transition-colors ${
          activeTab === 'product'
            ? 'text-black border-b-2 border-black'
            : 'text-text-secondary border-b border-text-secondary'
        }`}
      >
        Отзывы о товаре ({productReviewsCount})
      </button>

      {/* Company Reviews Tab */}
      <button
        onClick={() => handleTabChange('company')}
        className={`p-[10px] font-sans font-medium text-[14px] transition-colors ${
          activeTab === 'company'
            ? 'text-black border-b-2 border-black'
            : 'text-text-secondary border-b border-text-secondary'
        }`}
      >
        Отзывы о компании ({companyReviewsCount})
      </button>
    </div>
  );
}