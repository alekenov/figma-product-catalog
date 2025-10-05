import React from 'react';

/**
 * FeaturedProductCard - большая карточка товара для раздела "Хиты продаж"
 *
 * Дизайн из Figma: 352x499px карточка с акцентами
 *
 * @param {string} image - URL изображения товара
 * @param {string} price - Цена товара (с валютой)
 * @param {string} name - Название товара (макс 2 строки)
 * @param {string} deliveryText - Текст доставки (например "Завтра к 15:30")
 * @param {boolean} badge - Показать бейдж "Уже собрали"
 * @param {boolean} isFavorite - Флаг избранного
 * @param {function} onAddToCart - Колбэк при клике на кнопку "+"
 * @param {function} onFavoriteToggle - Колбэк при клике на избранное
 * @param {function} onClick - Колбэк при клике на карточку
 */
export default function FeaturedProductCard({
  image,
  price,
  name,
  deliveryText = 'Завтра к 15:30',
  badge = false,
  isFavorite = false,
  onAddToCart,
  onFavoriteToggle,
  onClick
}) {
  return (
    <div className="w-full max-w-[352px] h-[499px] relative flex flex-col gap-[16px]" data-testid="featured-product-card">
      {/* Product Image Container - точные размеры из Figma */}
      <div
        className="relative h-[384px] w-full cursor-pointer overflow-hidden rounded-[8px]"
        onClick={onClick}
      >
        <img
          alt={name}
          className="h-full w-full object-cover"
          src={image}
        />

        {/* Badge "Уже собрали" - точные размеры px/py из Figma */}
        {badge && (
          <div className="absolute top-[12px] left-[12px] bg-[#ff6666] rounded-full px-[12px] pt-[11px] pb-0 h-[40px] flex items-start">
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-white">
              Уже собрали
            </span>
          </div>
        )}

        {/* Favorite Icon - точная позиция из Figma */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavoriteToggle?.();
          }}
          className="absolute top-[12px] right-[12px] w-[24px] h-[24px] flex items-center justify-center"
          aria-label={isFavorite ? "Убрать из избранного" : "Добавить в избранное"}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.03L12 21.35Z"
              fill={isFavorite ? "#FF6666" : "white"}
              stroke={isFavorite ? "#FF6666" : "#E0E0E0"}
              strokeWidth="1"
            />
          </svg>
        </button>
      </div>

      {/* Price, Name and Add Button - точный gap [4px] из Figma */}
      <div className="flex items-start justify-between h-[74px]">
        <div className="flex flex-col gap-[4px] flex-1 max-w-[320px]">
          {/* Price - точная типографика из Figma */}
          <div className="font-['Open_Sans'] font-bold text-[18px] leading-[18px] text-[#212121] h-[18px]">
            {price}
          </div>

          {/* Product Name - точная типографика, 2 строки макс */}
          <button
            type="button"
            onClick={onClick}
            className="text-left font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[#212121] line-clamp-2 hover:text-[#ff6666] transition-colors w-full max-w-[253px]"
          >
            {name}
          </button>
        </div>

        {/* Add to Cart Button - точный размер 32x32px */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart?.();
          }}
          className="flex w-[32px] h-[32px] items-center justify-center flex-shrink-0"
          aria-label="Добавить в корзину"
        >
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="16" fill="#ff6666"/>
            <path
              d="M16 9.5V22.5M9.5 16H22.5"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>

      {/* Delivery Info - точный gap [4px] из Figma */}
      {deliveryText && (
        <div className="flex items-center gap-[4px] h-[21px]">
          {/* Truck Icon - точный размер 12x12px */}
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="shrink-0">
            <path
              d="M8.25 9.375C8.66421 9.375 9 9.03921 9 8.625C9 8.21079 8.66421 7.875 8.25 7.875C7.83579 7.875 7.5 8.21079 7.5 8.625C7.5 9.03921 7.83579 9.375 8.25 9.375Z"
              fill="#8F8F8F"
            />
            <path
              d="M3.75 9.375C4.16421 9.375 4.5 9.03921 4.5 8.625C4.5 8.21079 4.16421 7.875 3.75 7.875C3.33579 7.875 3 8.21079 3 8.625C3 9.03921 3.33579 9.375 3.75 9.375Z"
              fill="#8F8F8F"
            />
            <path
              d="M11.25 3.75H9L7.5 6.75H3V3.75H0.75V8.25H1.5C1.5 9.07843 2.17157 9.75 3 9.75C3.82843 9.75 4.5 9.07843 4.5 8.25H7.5C7.5 9.07843 8.17157 9.75 9 9.75C9.82843 9.75 10.5 9.07843 10.5 8.25H11.25V5.25L11.25 3.75Z"
              fill="#8F8F8F"
            />
          </svg>
          <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
            {deliveryText}
          </span>
        </div>
      )}
    </div>
  );
}
