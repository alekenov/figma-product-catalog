import React from 'react';

/**
 * DeliveryMethodSelector - выбор способа доставки (Доставка / Самовывоз)
 *
 * Дизайн из Figma: 352×113.75px секция с заголовком и двумя вариантами в ряд
 *
 * @param {string} selectedMethod - Выбранный метод ('delivery' или 'pickup')
 * @param {function} onChange - Колбэк при изменении метода доставки
 */
export default function DeliveryMethodSelector({
  selectedMethod = 'delivery',
  onChange
}) {
  return (
    <div className="flex flex-col gap-[16px] w-full">
      {/* Section Title */}
      <h3 className="font-['Open_Sans'] font-normal text-[18px] leading-[24.75px] text-[var(--text-primary)]">
        Способ доставки
      </h3>

      {/* Delivery Options */}
      <div className="flex gap-[8px] w-full">
        {/* Доставка */}
        <button
          onClick={() => onChange('delivery')}
          className={`flex-1 flex flex-col gap-[2px] px-[8px] py-[12px] rounded-[8px] border-2 transition-colors ${
            selectedMethod === 'delivery'
              ? 'border-[var(--brand-primary)] bg-white'
              : 'border-[var(--border-default)] bg-white hover:border-[var(--brand-primary)]'
          }`}
          style={{ height: '73px' }}
        >
          <div className="flex items-center justify-between">
            <span className="font-['Open_Sans'] font-normal text-[16px] leading-[24px] text-[var(--text-primary)]">
              Доставка
            </span>
            {/* Radio Button */}
            <div
              className={`w-[16px] h-[16px] rounded-full border-2 flex items-center justify-center transition-colors ${
                selectedMethod === 'delivery'
                  ? 'border-[var(--brand-primary)]'
                  : 'border-[var(--border-default)]'
              }`}
            >
              {selectedMethod === 'delivery' && (
                <div className="w-[10.66px] h-[10.66px]">
                  {/* Checkmark Icon */}
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                    <path
                      d="M9.16667 2.75L4.125 7.79167L1.83333 5.5"
                      stroke="var(--brand-primary)"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </div>
          </div>
          <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[var(--text-secondary)] text-left">
            от 30 мин.
          </span>
        </button>

        {/* Самовывоз */}
        <button
          onClick={() => onChange('pickup')}
          className={`flex-1 flex flex-col gap-[2px] px-[8px] py-[12px] rounded-[8px] border-2 transition-colors ${
            selectedMethod === 'pickup'
              ? 'border-[var(--brand-primary)] bg-white'
              : 'border-[var(--border-default)] bg-white hover:border-[var(--brand-primary)]'
          }`}
          style={{ height: '73px' }}
        >
          <div className="flex items-center justify-between">
            <span className="font-['Open_Sans'] font-normal text-[16px] leading-[24px] text-[var(--text-primary)]">
              Самовывоз
            </span>
            {/* Radio Button */}
            <div
              className={`w-[16px] h-[16px] rounded-full border-2 flex items-center justify-center transition-colors ${
                selectedMethod === 'pickup'
                  ? 'border-[var(--brand-primary)]'
                  : 'border-[var(--border-default)]'
              }`}
            >
              {selectedMethod === 'pickup' && (
                <div className="w-[10.66px] h-[10.66px]">
                  {/* Checkmark Icon */}
                  <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                    <path
                      d="M9.16667 2.75L4.125 7.79167L1.83333 5.5"
                      stroke="var(--brand-primary)"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </div>
          </div>
          <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[var(--text-secondary)] text-left">
            От 30 мин.
          </span>
        </button>
      </div>
    </div>
  );
}
