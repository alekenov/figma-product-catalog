import React, { useState } from 'react';
import PlatformReviewCard from './PlatformReviewCard';

/**
 * PlatformReviewsSection - секция отзывов о платформе
 *
 * Дизайн из Figma: Вертикальный список полноширинных карточек с заголовком и кнопкой
 *
 * @param {Array} reviews - Массив отзывов
 * @param {number} totalCount - Общее количество отзывов
 * @param {function} onShowAll - Колбэк при клике "Показать все"
 * @param {number} maxVisible - Сколько показывать изначально (по умолчанию 2)
 */
export default function PlatformReviewsSection({
  reviews = [],
  totalCount = 0,
  onShowAll,
  maxVisible = 2
}) {
  // Состояние для управления раскрытием длинных отзывов
  const [expandedReviews, setExpandedReviews] = useState(new Set());

  const handleToggleExpand = (reviewId) => {
    setExpandedReviews(prev => {
      const newSet = new Set(prev);
      if (newSet.has(reviewId)) {
        newSet.delete(reviewId);
      } else {
        newSet.add(reviewId);
      }
      return newSet;
    });
  };

  const handleLike = (reviewId) => {
    console.log('Like review:', reviewId);
    // TODO: Implement API integration when available
  };

  const handleDislike = (reviewId) => {
    console.log('Dislike review:', reviewId);
    // TODO: Implement API integration when available
  };

  const handleReply = (reviewId) => {
    console.log('Reply to review:', reviewId);
    // TODO: Implement reply functionality when available
  };

  // Показываем только первые maxVisible отзывов
  const visibleReviews = reviews.slice(0, maxVisible);

  return (
    <div className="flex flex-col gap-[16px] w-full">
      {/* Заголовок секции */}
      <div className="flex items-center justify-between h-[30.25px] w-full">
        <h2 className="font-['Open_Sans'] font-semibold text-[22px] leading-[30.25px] text-[#212121]">
          Отзывы покупателей
        </h2>
        <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
          {totalCount} {totalCount === 1 ? 'отзыв' : totalCount < 5 ? 'отзыва' : 'отзывов'}
        </span>
      </div>

      {/* Список карточек отзывов */}
      <div className="flex flex-col gap-[12px] w-full">
        {visibleReviews.length > 0 ? (
          visibleReviews.map(review => (
            <PlatformReviewCard
              key={review.id}
              authorName={review.authorName}
              date={review.date}
              rating={review.rating}
              reviewTitle={review.reviewTitle}
              text={review.text}
              isExpanded={expandedReviews.has(review.id)}
              hasReadMore={review.text && review.text.length > 150}
              likesCount={review.likesCount || 0}
              dislikesCount={review.dislikesCount || 0}
              onToggleExpand={() => handleToggleExpand(review.id)}
              onLike={() => handleLike(review.id)}
              onDislike={() => handleDislike(review.id)}
              onReply={() => handleReply(review.id)}
            />
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>Пока нет отзывов</p>
          </div>
        )}
      </div>

      {/* Кнопка "Показать все отзывов" */}
      {totalCount > maxVisible && onShowAll && (
        <div className="flex justify-center w-full">
          <button
            onClick={onShowAll}
            className="font-['Open_Sans'] font-normal text-[16px] leading-[16px] text-[#ff6666] px-[24px] py-[16px] rounded-[12px] hover:bg-[#fff5f5] transition-colors"
          >
            Показать все {totalCount} {totalCount === 1 ? 'отзыв' : totalCount < 5 ? 'отзыва' : 'отзывов'}
          </button>
        </div>
      )}
    </div>
  );
}
