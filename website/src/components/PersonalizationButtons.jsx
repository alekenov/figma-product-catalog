import React from 'react';

/**
 * PersonalizationButtons - кнопки для персонализации и добавления сертификата
 *
 * @param {function} onPersonalizationClick - Колбэк при клике на персонализацию
 * @param {function} onCertificateClick - Колбэк при клике на сертификат
 */
export default function PersonalizationButtons({ onPersonalizationClick, onCertificateClick }) {
  return (
    <div className="space-y-3">
      {/* Personalization Button */}
      <button
        onClick={onPersonalizationClick}
        className="w-full flex items-center gap-3 px-4 py-3 bg-bg-light rounded-lg hover:bg-bg-extra-light transition-colors"
      >
        {/* Edit Icon */}
        <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 flex-shrink-0">
          <path
            d="M14.5 2.5a2.121 2.121 0 0 1 3 3L6.5 16.5 2 18l1.5-4.5L14.5 2.5z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <span className="font-sans font-normal text-body-2 text-text-black text-left flex-1">
          Добавить данные для персонализации
        </span>
      </button>

      {/* Certificate Button */}
      <button
        onClick={onCertificateClick}
        className="w-full flex items-center gap-3 px-4 py-3 bg-bg-light rounded-lg hover:bg-bg-extra-light transition-colors"
      >
        {/* Certificate Icon */}
        <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5 flex-shrink-0">
          <path
            d="M10 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM7 18l3-3 3 3v-4a5 5 0 0 1-6 0v4z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <span className="font-sans font-normal text-body-2 text-text-black text-left flex-1">
          Добавить к заказу электронный сертификат
        </span>
      </button>
    </div>
  );
}