import React from 'react';

/**
 * CompositionSection - секция состава букета
 *
 * @param {Array} items - Массив элементов состава [{id, name, quantity}]
 */
export default function CompositionSection({ items }) {
  return (
    <div className="flex flex-col gap-4">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-[16px] text-text-black">
        Состав
      </h3>

      {/* Composition List */}
      <div className="flex flex-col gap-2">
        {items.map((item) => (
          <div key={item.id} className="flex gap-2 items-start">
            {/* Item Name */}
            <div className="font-sans font-normal text-[14px] text-text-black leading-[1.4]">
              {item.name}
            </div>

            {/* Dotted Line */}
            <div className="flex-1 font-sans font-normal text-[14px] text-[var(--text-muted)] leading-[1.4] overflow-hidden">
              .............................
            </div>

            {/* Quantity */}
            <div className="font-sans font-normal text-[14px] text-text-black leading-[1.4] whitespace-nowrap">
              {item.quantity} шт.
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
