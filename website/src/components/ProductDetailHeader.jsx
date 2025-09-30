import React from 'react';

/**
 * ProductDetailHeader - заголовок товара с бейджем размера
 *
 * @param {string} name - Название товара
 * @param {string} size - Размер товара (опционально)
 */
export default function ProductDetailHeader({ name, size }) {
  return (
    <div className="flex items-center justify-between gap-2">
      <h1 className="font-sans font-bold text-h2 text-text-black flex-1">
        {name}
      </h1>

      {size && (
        <span className="bg-bg-light px-3 py-1 rounded-full font-sans font-normal text-body-2 text-text-black whitespace-nowrap">
          {size}
        </span>
      )}
    </div>
  );
}