import React from 'react';

/**
 * TimeSlotPill - таблетка временного слота
 *
 * Дизайн из Figma: 102-110px × 39px таблетка с текстом и опциональным крестиком
 *
 * @param {string} label - Текст слота ("120-150 мин", "18:00-19:00")
 * @param {boolean} selected - Выбран ли слот
 * @param {function} onClick - Колбэк при клике на слот
 * @param {function} onRemove - Колбэк при клике на крестик (только для selected)
 */
export default function TimeSlotPill({
  label,
  selected = false,
  onClick,
  onRemove
}) {
  return (
    <button
      onClick={onClick}
      className={`relative flex items-center justify-center px-[13px] py-[9px] rounded-[16px] border transition-colors shrink-0 ${
        selected
          ? 'border-[var(--brand-primary)] bg-white'
          : 'border-[var(--border-default)] bg-white hover:border-[var(--brand-primary)]'
      }`}
      style={{ minHeight: '39px' }}
    >
      {/* Slot Label */}
      <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] ${
        selected ? 'text-[#212121]' : 'text-[#8f8f8f]'
      }`}>
        {label}
      </span>

      {/* Remove Icon (only when selected) */}
      {selected && onRemove && (
        <div
          role="button"
          tabIndex={0}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              e.stopPropagation();
              onRemove();
            }
          }}
          className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-[var(--brand-primary)] flex items-center justify-center hover:bg-[var(--brand-error)] transition-colors cursor-pointer"
          aria-label="Удалить выбор"
        >
          {/* X icon */}
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path
              d="M1 1L9 9M9 1L1 9"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
      )}
    </button>
  );
}
