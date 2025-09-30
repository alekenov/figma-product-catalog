import React, { useState } from 'react';

/**
 * ExpandableSection - раскрывающаяся секция (универсальный компонент)
 *
 * @param {string} title - Заголовок секции
 * @param {ReactNode} children - Содержимое секции
 * @param {boolean} defaultExpanded - Раскрыта по умолчанию
 */
export default function ExpandableSection({ title, children, defaultExpanded = false }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="border-t border-bg-light py-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between"
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
        <div className="pt-4">
          {children}
        </div>
      )}
    </div>
  );
}