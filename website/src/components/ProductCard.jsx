import React from 'react';

/**
 * ProductCard - карточка товара для главной страницы
 *
 * @param {string} image - URL изображения товара
 * @param {string} price - Цена товара (с валютой)
 * @param {string} name - Название товара
 * @param {string} deliveryText - Текст доставки (опционально)
 * @param {number} rating - Рейтинг товара (опционально)
 * @param {boolean} isFavorite - Флаг избранного (опционально)
 * @param {function} onAddToCart - Колбэк при клике на кнопку "+"
 * @param {function} onFavoriteToggle - Колбэк при клике на избранное
 * @param {function} onClick - Колбэк при клике на карточку
 */
export default function ProductCard({
  image,
  price,
  name,
  deliveryText,
  rating,
  isFavorite = false,
  onAddToCart,
  onFavoriteToggle,
  onClick
}) {
  return (
    <div className="w-[168px] relative" data-testid="product-card">
      {/* Product Image with Favorite Icon */}
      <div
        className="relative h-[221px] w-full cursor-pointer overflow-hidden rounded-[12px]"
        onClick={onClick}
      >
        <img
          alt={name}
          className="h-full w-full object-cover"
          src={image}
        />

        {/* Favorite Icon */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavoriteToggle?.();
          }}
          className="absolute top-2 right-2 w-[27px] h-6 flex items-center justify-center"
          aria-label="Добавить в избранное"
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

      {/* Price and Add Button */}
      <div className="mt-1 flex items-start justify-between h-[63px]">
        <div className="flex flex-col gap-1 flex-1">
          <div className="font-['Inter'] font-bold text-[16px] leading-6 tracking-[-0.3125px] text-black">
            {price}
          </div>

          <button
            type="button"
            onClick={onClick}
            className="text-left font-['Inter'] font-normal text-[14px] leading-[17.5px] tracking-[-0.1504px] text-black line-clamp-2 w-[108px] hover:text-[#FF6666]"
          >
            {name}
          </button>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart?.();
          }}
          className="flex size-8 items-center justify-center rounded-full transition-colors"
          aria-label="Добавить в корзину"
        >
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="16" fill="#FF6666"/>
            <path
              d="M16 9.5V22.5M9.5 16H22.5"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>

      {/* Delivery Info */}
      {deliveryText && (
        <div className="flex items-center gap-1 h-5 mt-1">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path
              d="M8.25 9.375C8.66421 9.375 9 9.03921 9 8.625C9 8.21079 8.66421 7.875 8.25 7.875C7.83579 7.875 7.5 8.21079 7.5 8.625C7.5 9.03921 7.83579 9.375 8.25 9.375Z"
              fill="#6A7282"
            />
            <path
              d="M3.75 9.375C4.16421 9.375 4.5 9.03921 4.5 8.625C4.5 8.21079 4.16421 7.875 3.75 7.875C3.33579 7.875 3 8.21079 3 8.625C3 9.03921 3.33579 9.375 3.75 9.375Z"
              fill="#6A7282"
            />
            <path
              d="M11.25 3.75H9L7.5 6.75H3V3.75H0.75V8.25H1.5C1.5 9.07843 2.17157 9.75 3 9.75C3.82843 9.75 4.5 9.07843 4.5 8.25H7.5C7.5 9.07843 8.17157 9.75 9 9.75C9.82843 9.75 10.5 9.07843 10.5 8.25H11.25V5.25L11.25 3.75Z"
              fill="#6A7282"
            />
          </svg>
          <span className="font-['Inter'] font-normal text-[14px] leading-5 tracking-[-0.1504px] text-[#6A7282]">
            {deliveryText}
          </span>
        </div>
      )}

      {/* Rating */}
      {rating && (
        <div className="flex items-center gap-0.5 h-5 mt-1">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path
              d="M6 0.75L7.854 4.521L12 5.133L9 8.061L9.708 12.18L6 10.221L2.292 12.18L3 8.061L0 5.133L4.146 4.521L6 0.75Z"
              fill="#FF6666"
            />
          </svg>
          <span className="font-['Inter'] font-normal text-[14px] leading-5 tracking-[-0.1504px] text-[#FF6666]">
            {rating}
          </span>
        </div>
      )}
    </div>
  );
}
