import React from 'react';

/**
 * AddToCartButton - большая розовая кнопка для добавления в корзину
 *
 * @param {string} price - Цена товара
 * @param {function} onClick - Колбэк при клике
 * @param {boolean} disabled - Кнопка неактивна
 */
export default function AddToCartButton({ price, onClick, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full py-4 px-6 rounded-lg font-sans font-bold text-button-normal transition-colors ${
        disabled
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
          : 'bg-pink text-white hover:opacity-90 active:scale-[0.98]'
      }`}
    >
      {price} в корзину
    </button>
  );
}