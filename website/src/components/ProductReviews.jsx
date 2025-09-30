import React from 'react';
import CvetyButton from './ui/CvetyButton';

/**
 * ProductReviewCard - карточка отзыва для страницы товара
 */
function ProductReviewCard({ rating, author, date, text, image }) {
  return (
    <div className="bg-bg-light rounded-lg p-4 space-y-3">
      {/* Image */}
      {image && (
        <div className="w-full h-32 rounded-md overflow-hidden">
          <img src={image} alt="Фото отзыва" className="w-full h-full object-cover" />
        </div>
      )}

      {/* Rating and Author */}
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          {/* Star Icon */}
          <svg viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4 text-yellow-400">
            <path d="M8 0l2.163 4.382 4.837.703-3.5 3.411.826 4.816L8 11.236l-4.326 2.076.826-4.816-3.5-3.411 4.837-.703L8 0z" />
          </svg>
          <span className="font-sans font-bold text-body-2 text-text-black">{rating}</span>
        </div>

        <p className="font-sans font-bold text-body-2 text-text-black">{author}</p>
        <p className="font-sans font-normal text-field-title text-text-grey-dark">{date}</p>
      </div>

      {/* Review Text */}
      <p className="font-sans font-normal text-body-2 text-text-black">{text}</p>
    </div>
  );
}

/**
 * ProductReviews - секция отзывов о товаре
 *
 * @param {Array} reviews - Массив отзывов
 * @param {function} onShowAll - Колбэк при клике "Показать все"
 */
export default function ProductReviews({ reviews, onShowAll }) {
  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="font-sans font-bold text-h3 text-text-black">
          Отзывы о букете
        </h2>

        {onShowAll && (
          <CvetyButton
            variant="link"
            size="sm"
            onClick={onShowAll}
            className="text-body-2"
          >
            Все
          </CvetyButton>
        )}
      </div>

      {/* Reviews Grid */}
      <div className="grid grid-cols-2 gap-3">
        {reviews.map((review) => (
          <ProductReviewCard key={review.id} {...review} />
        ))}
      </div>
    </div>
  );
}