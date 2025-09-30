import React, { useState } from 'react';

/**
 * ColorSelector - выбор цвета товара
 *
 * @param {Array} colors - Массив доступных цветов [{ id, name, hex }]
 * @param {number} selectedColorId - ID выбранного цвета
 * @param {function} onColorSelect - Колбэк при выборе цвета
 */
export default function ColorSelector({ colors, selectedColorId, onColorSelect }) {
  return (
    <div className="space-y-3">
      <h3 className="font-sans font-normal text-body-2 text-text-black">
        Выберите цвет
      </h3>

      <div className="flex gap-2">
        {colors.map((color) => (
          <button
            key={color.id}
            onClick={() => onColorSelect(color.id)}
            className={`w-10 h-10 rounded-full transition-all ${
              selectedColorId === color.id
                ? 'ring-2 ring-offset-2 ring-main-pink'
                : 'hover:ring-2 hover:ring-offset-2 hover:ring-bg-light'
            }`}
            style={{ backgroundColor: color.hex }}
            aria-label={`Выбрать цвет ${color.name}`}
            title={color.name}
          />
        ))}
      </div>
    </div>
  );
}