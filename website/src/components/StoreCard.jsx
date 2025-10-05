import React from 'react';

/**
 * StoreCard - карточка магазина для секции "Популярные магазины"
 *
 * Дизайн из Figma: 320x262.75px карточка с информацией о магазине
 *
 * @param {string} image - URL изображения магазина
 * @param {string} badgeText - Текст бейджа ("Лучший рейтинг", "Быстрая доставка")
 * @param {string} badgeColor - Цвет бейджа ("green" по умолчанию)
 * @param {string} name - Название магазина
 * @param {number} rating - Рейтинг магазина (0-5)
 * @param {number} reviewsCount - Количество отзывов
 * @param {string} status - Статус магазина ("open", "closed", "closing_soon")
 * @param {string} statusText - Текст статуса ("Открыт", "До 8:00")
 * @param {string} deliveryTime - Время доставки ("25 мин", "30 мин")
 * @param {string} deliveryPrice - Цена доставки ("1500 ₸", "Бесплатно")
 * @param {function} onClick - Колбэк при клике на карточку
 */
export default function StoreCard({
  image,
  badgeText,
  badgeColor = 'green',
  name,
  rating,
  reviewsCount,
  status = 'open',
  statusText,
  deliveryTime,
  deliveryPrice,
  onClick
}) {
  // Определяем цвет статуса
  const statusColors = {
    open: { dot: '#01bc6f', text: '#01bc6f' },
    closed: { dot: '#ff4444', text: '#ff4444' },
    closing_soon: { dot: '#ff4444', text: '#ff4444' }
  };

  const currentStatus = statusColors[status] || statusColors.open;
  const isDeliveryFree = deliveryPrice === 'Бесплатно';

  return (
    <div
      className="bg-white box-border flex flex-col gap-[12px] h-[262.75px] pt-[16px] px-[16px] pb-0 rounded-[8px] w-full cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      {/* Image Container */}
      <div className="h-[128px] overflow-hidden rounded-[8px] relative w-full">
        <img
          alt={name}
          className="h-full w-full object-cover"
          src={image}
        />

        {/* Badge */}
        {badgeText && (
          <div className="absolute top-[8px] left-[8px] bg-[#01bc6f] rounded-full px-[12px] py-[4px] h-[26px] flex items-center">
            <span className="font-['Open_Sans'] font-normal text-[12px] leading-[18px] text-white">
              {badgeText}
            </span>
          </div>
        )}
      </div>

      {/* Store Info */}
      <div className="flex flex-col gap-[8px] h-[90.75px] w-full">
        {/* Store Name and Rating */}
        <div className="flex items-start justify-between h-[24.75px] w-full">
          <div className="flex-1 h-[24.75px] overflow-hidden">
            <p className="font-['Open_Sans'] font-normal text-[18px] leading-[24.75px] text-[#212121] truncate">
              {name}
            </p>
          </div>

          {/* Rating */}
          <div className="flex items-center gap-[4px] h-[24px] ml-2">
            {/* Star Icon */}
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="shrink-0">
              <path
                d="M8 1.33333L9.88 5.14667L14 5.74667L11 8.66667L11.72 12.7733L8 10.78L4.28 12.7733L5 8.66667L2 5.74667L6.12 5.14667L8 1.33333Z"
                fill="#FFB800"
              />
            </svg>
            <span className="font-['Open_Sans'] font-normal text-[16px] leading-[24px] text-[#212121]">
              {rating.toFixed(1)}
            </span>
          </div>
        </div>

        {/* Reviews and Status */}
        <div className="flex items-center justify-between h-[21px] w-full">
          <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
            {reviewsCount} отзывов
          </span>

          {/* Status */}
          <div className="flex items-center gap-[4px] h-[21px]">
            <div
              className="w-[8px] h-[8px] rounded-full"
              style={{ backgroundColor: currentStatus.dot }}
            />
            <span
              className="font-['Open_Sans'] font-normal text-[14px] leading-[21px]"
              style={{ color: currentStatus.text }}
            >
              {statusText}
            </span>
          </div>
        </div>

        {/* Delivery Info */}
        <div className="border-t border-[#eeeeee] flex items-center justify-between h-[29px] pt-[1px] w-full">
          <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
            Доставка {deliveryTime}
          </span>
          <span
            className="font-['Open_Sans'] font-normal text-[16px] leading-[24px]"
            style={{ color: isDeliveryFree ? '#01bc6f' : '#212121' }}
          >
            {deliveryPrice}
          </span>
        </div>
      </div>
    </div>
  );
}
