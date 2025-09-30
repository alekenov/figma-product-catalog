import React from 'react';

/**
 * DeliveryTimeSelector - выбор времени доставки
 *
 * @param {string} deliveryType - Тип доставки ('express' или 'scheduled')
 * @param {string} scheduledTime - Время для запланированной доставки (например, "30.03.24 к 12:30")
 * @param {function} onDeliveryTypeChange - Колбэк при изменении типа доставки
 * @param {function} onScheduledTimeChange - Колбэк при изменении времени (опционально)
 */
export default function DeliveryTimeSelector({
  deliveryType = 'express',
  scheduledTime = '',
  onDeliveryTypeChange,
  onScheduledTimeChange
}) {
  return (
    <div className="space-y-3">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-body-1 text-text-black">
        Дата и время
      </h3>

      {/* Delivery Options */}
      <div className="flex gap-3">
        {/* Express Delivery */}
        <button
          onClick={() => onDeliveryTypeChange('express')}
          className={`flex-1 flex flex-col gap-3 px-2 py-3 rounded-lg border-2 transition-colors ${
            deliveryType === 'express'
              ? 'border-pink bg-white'
              : 'border-bg-light bg-white'
          }`}
        >
          <div className="flex items-center justify-between px-2">
            <span className="font-sans font-normal text-body-2 text-text-black">
              Экспресс
            </span>
            <div
              className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                deliveryType === 'express'
                  ? 'border-pink'
                  : 'border-bg-light'
              }`}
            >
              {deliveryType === 'express' && (
                <div className="w-2 h-2 rounded-full bg-pink" />
              )}
            </div>
          </div>
          <span className="font-sans font-normal text-field-title text-text-grey-dark px-2 text-left">
            30 мин
          </span>
        </button>

        {/* Scheduled Delivery */}
        <button
          onClick={() => onDeliveryTypeChange('scheduled')}
          className={`flex-1 flex flex-col gap-3 px-2 py-3 rounded-lg border-2 transition-colors ${
            deliveryType === 'scheduled'
              ? 'border-pink bg-white'
              : 'border-bg-light bg-white'
          }`}
        >
          <div className="flex items-center justify-between px-2">
            <span className="font-sans font-normal text-body-2 text-text-black">
              По расписанию
            </span>
            <div
              className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                deliveryType === 'scheduled'
                  ? 'border-pink'
                  : 'border-bg-light'
              }`}
            >
              {deliveryType === 'scheduled' && (
                <div className="w-2 h-2 rounded-full bg-pink" />
              )}
            </div>
          </div>
          <span className="font-sans font-normal text-field-title text-text-grey-dark px-2 text-left">
            {scheduledTime || '31.03.24 в 12:30'}
          </span>
        </button>
      </div>

      {/* Scheduled Time Input (shown when scheduled is selected) */}
      {deliveryType === 'scheduled' && onScheduledTimeChange && (
        <input
          type="text"
          value={scheduledTime}
          onChange={(e) => onScheduledTimeChange(e.target.value)}
          placeholder="Выберите дату и время"
          className="w-full px-4 py-3 rounded-lg border border-bg-light bg-white font-sans font-normal text-body-2 text-text-black placeholder:text-text-grey-dark focus:outline-none focus:border-pink transition-colors"
        />
      )}
    </div>
  );
}