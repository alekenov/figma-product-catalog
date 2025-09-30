import React from 'react';
import CvetyCheckbox from './ui/CvetyCheckbox';

/**
 * AdditionalOptions - дополнительные опции с чекбоксами
 *
 * @param {string} title - Заголовок секции (например, "Дополнительно")
 * @param {Array} options - Массив опций [{id, label, checked}]
 * @param {function} onOptionToggle - Колбэк при изменении чекбокса
 */
export default function AdditionalOptions({ title = 'Дополнительно', options, onOptionToggle }) {
  return (
    <div className="flex flex-col gap-4">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-[16px] text-text-black">
        {title}
      </h3>

      {/* Options List */}
      <div className="flex flex-col gap-2">
        {options.map((option) => (
          <CvetyCheckbox
            key={option.id}
            checked={option.checked}
            onChange={(checked) => onOptionToggle(option.id, checked)}
            label={option.label}
            size="md"
          />
        ))}
      </div>
    </div>
  );
}
