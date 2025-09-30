import React, { useState } from 'react';
import CvetyCheckbox from './ui/CvetyCheckbox';

/**
 * PickupSection - секция самовывоза с чекбоксом и раскрывающимся списком адресов
 *
 * @param {boolean} checked - Состояние чекбокса
 * @param {function} onChange - Колбэк при изменении чекбокса
 * @param {Array} addresses - Массив адресов для самовывоза
 */
export default function PickupSection({ checked, onChange, addresses = [] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="space-y-3">
      {/* Checkbox */}
      <CvetyCheckbox
        checked={checked}
        onChange={onChange}
        label={`Самовывоз по ${addresses.length} адресу`}
        size="sm"
      />

      {/* Expandable Addresses List */}
      {checked && addresses.length > 0 && (
        <div className="pl-7 space-y-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="font-sans font-normal text-body-2 text-pink hover:underline"
          >
            {isExpanded ? 'Скрыть адреса' : 'Показать адреса'}
          </button>

          {isExpanded && (
            <div className="space-y-2 pt-2">
              {addresses.map((address, index) => (
                <div
                  key={index}
                  className="font-sans font-normal text-body-2 text-text-grey-dark"
                >
                  {address}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}