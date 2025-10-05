import React from 'react';
import TimeSlotPill from './TimeSlotPill';

/**
 * DateTimeSelector - выбор даты и времени доставки
 *
 * Дизайн из Figma: 352×150.75px секция с табами даты и слотами времени
 *
 * @param {string} selectedDate - Выбранная дата ('today', 'tomorrow')
 * @param {function} onDateChange - Колбэк при изменении даты
 * @param {string} selectedTime - Выбранный временной слот
 * @param {function} onTimeChange - Колбэк при изменении времени
 */
export default function DateTimeSelector({
  selectedDate = 'today',
  onDateChange,
  selectedTime = '',
  onTimeChange
}) {
  // Временные слоты для демонстрации
  const timeSlots = [
    { id: '120-150', label: '120-150 мин' },
    { id: '18-19', label: '18:00-19:00' },
    { id: '19-20', label: '19:00-20:00' },
    { id: '20-21', label: '20:00-21:00' }
  ];

  return (
    <div className="flex flex-col gap-[16px] w-full">
      {/* Section Title */}
      <h3 className="font-['Open_Sans'] font-normal text-[18px] leading-[24.75px] text-[var(--text-primary)]">
        Дата и время
      </h3>

      {/* Date Tabs */}
      <div className="flex items-center gap-[8px] w-full" style={{ height: '39px' }}>
        {/* Calendar Icon */}
        <div className="flex items-center justify-center w-[32px] h-[32px] bg-black rounded-full">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect
              x="2"
              y="3.33333"
              width="12"
              height="10.6667"
              rx="1.33333"
              stroke="white"
              strokeWidth="1.5"
            />
            <path
              d="M2 6.66667H14"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <path
              d="M5.33333 2V4.66667"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <path
              d="M10.6667 2V4.66667"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>

        {/* Date Tabs Container */}
        <div className="flex gap-[4px]">
          {/* Сегодня */}
          <button
            onClick={() => onDateChange('today')}
            className={`relative flex items-center gap-[8px] px-[17px] py-[9px] rounded-[16px] border transition-colors ${
              selectedDate === 'today'
                ? 'border-[var(--brand-primary)] bg-white'
                : 'border-[var(--border-default)] bg-white hover:border-[var(--brand-primary)]'
            }`}
            style={{ height: '39px' }}
          >
            {/* Calendar icon */}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect
                x="1.75"
                y="2.91667"
                width="10.5"
                height="9.33333"
                rx="1.16667"
                stroke={selectedDate === 'today' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
              />
              <path
                d="M1.75 5.83333H12.25"
                stroke={selectedDate === 'today' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M4.66667 1.75V4.08333"
                stroke={selectedDate === 'today' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M9.33333 1.75V4.08333"
                stroke={selectedDate === 'today' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
            </svg>
            <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] ${
              selectedDate === 'today' ? 'text-[#212121]' : 'text-[#8f8f8f]'
            }`}>
              Сегодня
            </span>

            {/* Remove button (only when selected) */}
            {selectedDate === 'today' && (
              <div
                role="button"
                tabIndex={0}
                onClick={(e) => {
                  e.stopPropagation();
                  onDateChange('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    onDateChange('');
                  }
                }}
                className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-[var(--brand-primary)] flex items-center justify-center hover:bg-[var(--brand-error)] transition-colors cursor-pointer"
                aria-label="Очистить выбор"
              >
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

          {/* Завтра */}
          <button
            onClick={() => onDateChange('tomorrow')}
            className={`relative flex items-center gap-[8px] px-[17px] py-[9px] rounded-[16px] border transition-colors ${
              selectedDate === 'tomorrow'
                ? 'border-[var(--brand-primary)] bg-white'
                : 'border-[var(--border-default)] bg-white hover:border-[var(--brand-primary)]'
            }`}
            style={{ height: '39px' }}
          >
            {/* Calendar icon */}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect
                x="1.75"
                y="2.91667"
                width="10.5"
                height="9.33333"
                rx="1.16667"
                stroke={selectedDate === 'tomorrow' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
              />
              <path
                d="M1.75 5.83333H12.25"
                stroke={selectedDate === 'tomorrow' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M4.66667 1.75V4.08333"
                stroke={selectedDate === 'tomorrow' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M9.33333 1.75V4.08333"
                stroke={selectedDate === 'tomorrow' ? '#212121' : '#8f8f8f'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
            </svg>
            <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] ${
              selectedDate === 'tomorrow' ? 'text-[#212121]' : 'text-[#8f8f8f]'
            }`}>
              Завтра
            </span>

            {/* Remove button (only when selected) */}
            {selectedDate === 'tomorrow' && (
              <div
                role="button"
                tabIndex={0}
                onClick={(e) => {
                  e.stopPropagation();
                  onDateChange('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    onDateChange('');
                  }
                }}
                className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-[var(--brand-primary)] flex items-center justify-center hover:bg-[var(--brand-error)] transition-colors cursor-pointer"
                aria-label="Очистить выбор"
              >
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
        </div>
      </div>

      {/* Time Slots - Horizontal Scroll */}
      <div className="w-full overflow-x-auto" style={{ height: '55px' }}>
        <div className="flex gap-[8px] py-[8px]">
          {timeSlots.map((slot) => (
            <TimeSlotPill
              key={slot.id}
              label={slot.label}
              selected={selectedTime === slot.id}
              onClick={() => onTimeChange(slot.id)}
              onRemove={() => onTimeChange('')}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
