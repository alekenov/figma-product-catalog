import React from 'react';
import CvetyButton from './ui/CvetyButton';

/**
 * SectionHeader - заголовок секции с кнопкой "Показать всё"
 *
 * @param {string} title - Заголовок секции
 * @param {function} onShowAll - Колбэк при клике на "Показать всё"
 * @param {boolean} showButton - Показывать ли кнопку "Показать всё" (по умолчанию true)
 */
export default function SectionHeader({ title, onShowAll, showButton = true }) {
  return (
    <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
      {/* Section Title */}
      <h2 className="font-sans font-bold leading-normal text-h2 text-text-black">
        {title}
      </h2>

      {/* Show All Button */}
      {showButton && onShowAll && (
        <CvetyButton
          variant="link"
          size="sm"
          onClick={onShowAll}
          className="whitespace-nowrap text-body-2"
        >
          Показать всё
        </CvetyButton>
      )}
    </div>
  );
}