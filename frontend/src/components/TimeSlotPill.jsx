import React from 'react';

/**
 * TimeSlotPill - таблетка временного слота для админ-панели
 *
 * @param {string} label - Текст слота ("09:00-11:00", "11:00-13:00")
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
      type="button"
      onClick={onClick}
      className={`relative flex items-center justify-center px-[13px] py-[9px] rounded-[16px] border transition-colors shrink-0 ${
        selected
          ? 'border-purple-primary bg-white'
          : 'border-gray-border bg-white hover:border-purple-primary'
      }`}
      style={{ minHeight: '39px' }}
    >
      {/* Slot Label */}
      <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] ${
        selected ? 'text-black' : 'text-gray-disabled'
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
          className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-purple-primary flex items-center justify-center hover:bg-red-600 transition-colors cursor-pointer"
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
