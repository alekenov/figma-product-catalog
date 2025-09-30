import React from 'react';
import CvetyCheckbox from './ui/CvetyCheckbox';

/**
 * GuaranteeCheckbox - чекбокс гарантии лучшей цены
 *
 * @param {boolean} checked - Состояние чекбокса
 * @param {function} onChange - Колбэк при изменении
 * @param {string} title - Заголовок
 * @param {string} subtitle - Подзаголовок
 */
export default function GuaranteeCheckbox({ checked, onChange, title, subtitle }) {
  return (
    <div className="flex items-start gap-3">
      {/* Gift Icon */}
      <div className="flex-shrink-0 w-6 h-6 mt-0.5">
        <svg viewBox="0 0 24 24" fill="none" className="w-full h-full">
          <path
            d="M20 12v10H4V12M2 7h20v5H2V7zM12 22V7M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Text Content with Checkbox */}
      <div className="flex-1">
        <CvetyCheckbox
          checked={checked}
          onChange={onChange}
          label={title}
          size="sm"
        />

        {/* Subtitle */}
        {subtitle && (
          <p className="font-sans font-normal text-field-title text-text-grey-dark mt-1 ml-6">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}