import React from 'react';

/**
 * SizeSelector - селектор размеров товара с ценами
 *
 * @param {Array} sizes - Массив размеров [{id, label, price}]
 * @param {string|number} selectedSize - ID выбранного размера
 * @param {function} onSizeSelect - Колбэк при выборе размера
 */
export default function SizeSelector({ sizes, selectedSize, onSizeSelect }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {sizes.map((size) => (
        <button
          key={size.id}
          onClick={() => onSizeSelect(size.id)}
          className={`flex flex-col items-center justify-center py-[12px] px-2 rounded-[6px] border transition-all ${
            selectedSize === size.id
              ? 'border-black'
              : 'border-[var(--border-default)] hover:border-black'
          }`}
        >
          {/* Size Label */}
          <span className="font-sans font-semibold text-[14px] text-text-black">
            {size.label}
          </span>

          {/* Price */}
          <span className="font-sans font-semibold text-[16px] text-text-black">
            {size.price}
          </span>
        </button>
      ))}
    </div>
  );
}
