import React from 'react';

/**
 * ActualTodayBanner - баннер "Актуально сегодня"
 *
 * @param {string} text - Текст баннера
 */
export default function ActualTodayBanner({ text }) {
  return (
    <div className="bg-bg-light rounded-lg p-4 space-y-2">
      {/* Header with Icon */}
      <div className="flex items-center gap-2">
        {/* Alert Icon */}
        <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 text-text-pink flex-shrink-0">
          <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2" />
          <path
            d="M10 6v4M10 14h.01"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>

        <span className="font-sans font-bold text-body-2 text-text-pink uppercase">
          Актуально сегодня
        </span>
      </div>

      {/* Content Text */}
      <p className="font-sans font-normal text-body-2 text-text-black whitespace-pre-line">
        {text}
      </p>
    </div>
  );
}