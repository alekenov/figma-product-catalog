import React from 'react';

/**
 * ProductHeaderWithRating - заголовок товара с рейтингом и статистикой
 *
 * @param {string} name - Название товара
 * @param {number} rating - Средний рейтинг (например, 4.6)
 * @param {number} reviewCount - Количество отзывов
 * @param {number} ratingCount - Количество оценок
 * @param {string} size - Размер товара (например, "1-20 см")
 */
export default function ProductHeaderWithRating({
  name,
  rating,
  reviewCount,
  ratingCount,
  size
}) {
  return (
    <div className="space-y-2">
      {/* Product Name */}
      <h1 className="font-sans font-bold text-h2 text-text-black">
        {name}
      </h1>

      {/* Rating and Stats Row */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Rating with Star */}
        <div className="flex items-center gap-1">
          <svg viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4 text-yellow-400">
            <path d="M8 0l2.163 4.382 4.837.703-3.5 3.411.826 4.816L8 11.236l-4.326 2.076.826-4.816-3.5-3.411 4.837-.703L8 0z" />
          </svg>
          <span className="font-sans font-normal text-body-2 text-text-black">
            {rating}
          </span>
        </div>

        {/* Divider */}
        <span className="text-text-grey-dark">•</span>

        {/* Review Count */}
        <span className="font-sans font-normal text-body-2 text-text-grey-dark">
          {reviewCount} отзыва
        </span>

        {/* Divider */}
        <span className="text-text-grey-dark">•</span>

        {/* Rating Count */}
        <span className="font-sans font-normal text-body-2 text-text-grey-dark">
          {ratingCount} оценок
        </span>

        {/* Size Badge */}
        {size && (
          <>
            <span className="text-text-grey-dark">•</span>
            <span className="bg-bg-light px-3 py-1 rounded-full font-sans font-normal text-body-2 text-text-black">
              {size}
            </span>
          </>
        )}
      </div>
    </div>
  );
}