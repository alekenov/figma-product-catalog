import React from 'react';
import TimeSlotPill from './TimeSlotPill';

/**
 * DateTimeSelectorAdmin - выбор даты и времени доставки для админ-панели
 *
 * @param {string} selectedDate - Выбранная дата ('today', 'tomorrow')
 * @param {function} onDateChange - Колбэк при изменении даты
 * @param {string} selectedTime - Выбранный временной слот
 * @param {function} onTimeChange - Колбэк при изменении времени
 */
export default function DateTimeSelectorAdmin({
  selectedDate = 'today',
  onDateChange,
  selectedTime = '',
  onTimeChange
}) {
  // Временные слоты для доставки
  const timeSlots = [
    { id: '09:00-11:00', label: '09:00-11:00' },
    { id: '11:00-13:00', label: '11:00-13:00' },
    { id: '13:00-15:00', label: '13:00-15:00' },
    { id: '15:00-17:00', label: '15:00-17:00' },
    { id: '17:00-19:00', label: '17:00-19:00' },
    { id: '19:00-21:00', label: '19:00-21:00' }
  ];

  return (
    <div className="flex flex-col gap-[16px] w-full">
      {/* Date Tabs */}
      <div className="flex items-center gap-[8px] w-full" style={{ minHeight: '39px' }}>
        {/* Calendar Icon */}
        <div className="flex items-center justify-center w-[32px] h-[32px] bg-black rounded-full shrink-0">
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
        <div className="flex gap-[4px] overflow-x-auto">
          {/* Сегодня */}
          <button
            type="button"
            onClick={() => onDateChange('today')}
            className={`relative flex items-center gap-[8px] px-[17px] py-[9px] rounded-[16px] border transition-colors shrink-0 ${
              selectedDate === 'today'
                ? 'border-purple-primary bg-white'
                : 'border-gray-border bg-white hover:border-purple-primary'
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
                stroke={selectedDate === 'today' ? '#000000' : '#828282'}
                strokeWidth="1.3"
              />
              <path
                d="M1.75 5.83333H12.25"
                stroke={selectedDate === 'today' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M4.66667 1.75V4.08333"
                stroke={selectedDate === 'today' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M9.33333 1.75V4.08333"
                stroke={selectedDate === 'today' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
            </svg>
            <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] whitespace-nowrap ${
              selectedDate === 'today' ? 'text-black' : 'text-gray-disabled'
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
                className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-purple-primary flex items-center justify-center hover:bg-red-600 transition-colors cursor-pointer"
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
            type="button"
            onClick={() => onDateChange('tomorrow')}
            className={`relative flex items-center gap-[8px] px-[17px] py-[9px] rounded-[16px] border transition-colors shrink-0 ${
              selectedDate === 'tomorrow'
                ? 'border-purple-primary bg-white'
                : 'border-gray-border bg-white hover:border-purple-primary'
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
                stroke={selectedDate === 'tomorrow' ? '#000000' : '#828282'}
                strokeWidth="1.3"
              />
              <path
                d="M1.75 5.83333H12.25"
                stroke={selectedDate === 'tomorrow' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M4.66667 1.75V4.08333"
                stroke={selectedDate === 'tomorrow' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
              <path
                d="M9.33333 1.75V4.08333"
                stroke={selectedDate === 'tomorrow' ? '#000000' : '#828282'}
                strokeWidth="1.3"
                strokeLinecap="round"
              />
            </svg>
            <span className={`font-['Open_Sans'] font-normal text-[14px] leading-[21px] whitespace-nowrap ${
              selectedDate === 'tomorrow' ? 'text-black' : 'text-gray-disabled'
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
                className="absolute top-[-3px] right-[-3px] w-[16px] h-[16px] rounded-full bg-purple-primary flex items-center justify-center hover:bg-red-600 transition-colors cursor-pointer"
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
      <div className="w-full overflow-x-auto" style={{ minHeight: '47px' }}>
        <div className="flex gap-[8px]">
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
