import React from 'react';

/**
 * ProductCard - карточка товара для главной страницы
 *
 * @param {string} image - URL изображения товара
 * @param {string} price - Цена товара (с валютой)
 * @param {string} name - Название товара
 * @param {string} deliveryText - Текст доставки (опционально)
 * @param {function} onAddToCart - Колбэк при клике на кнопку "+"
 * @param {function} onClick - Колбэк при клике на карточку
 */
export default function ProductCard({
  image,
  price,
  name,
  deliveryText,
  onAddToCart,
  onClick
}) {
  return (
    <div className="content-stretch flex flex-col gap-1 items-start relative w-full">
      {/* Product Image */}
      <div
        className="h-[268px] relative rounded-md shrink-0 w-full cursor-pointer overflow-hidden"
        onClick={onClick}
      >
        <img
          alt={name}
          className="w-full h-full object-cover"
          src={image}
        />
      </div>

      {/* Product Info */}
      <div className="content-stretch flex gap-1 items-start relative shrink-0 w-full">
        {/* Text Content */}
        <div className="content-stretch flex flex-1 flex-col gap-1 items-start relative shrink-0 min-w-0">
          {/* Price */}
          <div className="content-stretch flex gap-2 items-center relative shrink-0">
            <div className="font-sans font-bold leading-normal text-h4 text-text-black whitespace-nowrap">
              {price}
            </div>
          </div>

          {/* Name and Delivery */}
          <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0 w-full">
            {/* Product Name */}
            <div
              className="font-sans font-normal leading-normal text-body-2 text-text-black line-clamp-2 cursor-pointer"
              onClick={onClick}
            >
              {name}
            </div>

            {/* Delivery Text */}
            {deliveryText && (
              <div className="font-sans font-normal leading-normal text-field-title text-text-grey-dark whitespace-nowrap">
                {deliveryText}
              </div>
            )}
          </div>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAddToCart?.();
          }}
          className="bg-bg-light box-border content-stretch flex items-center justify-center p-2 relative rounded-full shrink-0 size-8 hover:bg-bg-extra-light transition-colors"
          aria-label="Добавить в корзину"
        >
          <svg
            width="13"
            height="13"
            viewBox="0 0 13 13"
            fill="none"
            className="relative shrink-0"
          >
            <path
              d="M6.5 1V12M1 6.5H12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}