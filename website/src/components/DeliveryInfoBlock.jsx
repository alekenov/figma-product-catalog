import React from 'react';

/**
 * DeliveryInfoBlock - блок информации о доставке
 *
 * @param {string} title - Заголовок (например, "Точно доставим - Астана")
 * @param {string} address - Адрес доставки
 * @param {string} price - Стоимость доставки
 * @param {string} time - Время доставки
 */
export default function DeliveryInfoBlock({ title, address, price, time }) {
  return (
    <div className="bg-blue-50 rounded-lg p-4 space-y-3">
      {/* Header with Clock Icon */}
      <div className="flex items-center gap-2">
        {/* Clock Icon */}
        <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 text-blue-600 flex-shrink-0">
          <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2" />
          <path
            d="M10 5v5l3 3"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <span className="font-sans font-bold text-body-2 text-blue-900">
          {title}
        </span>
      </div>

      {/* Delivery Details */}
      <div className="space-y-1 font-sans font-normal text-body-2 text-blue-900">
        <p>{address}</p>
        <p className="font-bold">{price}</p>
        <p>Ближайшая дата: {time}</p>
      </div>
    </div>
  );
}