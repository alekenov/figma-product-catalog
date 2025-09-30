import React, { useState } from 'react';

/**
 * ProductDescription - раскрывающееся описание товара
 *
 * @param {string} title - Заголовок секции (например, "Описание")
 * @param {string} content - Текст описания
 */
export default function ProductDescription({ title = 'Описание', content }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border-t border-bg-light pt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-2"
      >
        <span className="font-sans font-bold text-body-1 text-text-black">
          {title}
        </span>

        {/* Chevron Icon */}
        <svg
          viewBox="0 0 20 20"
          fill="none"
          className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="py-4 font-sans font-normal text-body-2 text-text-black whitespace-pre-line">
          {content}
        </div>
      )}
    </div>
  );
}