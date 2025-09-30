import React, { useState } from 'react';
import CvetyButton from './ui/CvetyButton';

/**
 * DetailedReviewsSection - полная секция отзывов с рейтингом, фото и отзывами
 *
 * @param {number} averageRating - Средний рейтинг (например, 4.8)
 * @param {number} totalReviews - Общее количество отзывов
 * @param {Object} ratingBreakdown - Разбивка по звездам {5: 45, 4: 10, 3: 2, 2: 0, 1: 1}
 * @param {Array} reviewPhotos - Массив фото из отзывов [{id, url}]
 * @param {Array} reviews - Массив отзывов [{id, author, avatar, date, rating, text, photos, likes, dislikes}]
 * @param {function} onLoadMore - Колбэк для загрузки дополнительных отзывов
 * @param {boolean} hasMore - Есть ли ещё отзывы для загрузки
 */
export default function DetailedReviewsSection({
  averageRating,
  totalReviews,
  ratingBreakdown = {},
  reviewPhotos = [],
  reviews = [],
  onLoadMore,
  hasMore = false
}) {
  const [likedReviews, setLikedReviews] = useState([]);
  const [dislikedReviews, setDislikedReviews] = useState([]);

  const handleLike = (reviewId) => {
    if (dislikedReviews.includes(reviewId)) {
      setDislikedReviews(dislikedReviews.filter(id => id !== reviewId));
    }
    if (likedReviews.includes(reviewId)) {
      setLikedReviews(likedReviews.filter(id => id !== reviewId));
    } else {
      setLikedReviews([...likedReviews, reviewId]);
    }
  };

  const handleDislike = (reviewId) => {
    if (likedReviews.includes(reviewId)) {
      setLikedReviews(likedReviews.filter(id => id !== reviewId));
    }
    if (dislikedReviews.includes(reviewId)) {
      setDislikedReviews(dislikedReviews.filter(id => id !== reviewId));
    } else {
      setDislikedReviews([...dislikedReviews, reviewId]);
    }
  };

  // Функция для склонения слова "отзыв"
  const getReviewWord = (count) => {
    if (count % 10 === 1 && count % 100 !== 11) return 'отзыв';
    if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'отзыва';
    return 'отзывов';
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Rating Summary */}
      <div className="border-b border-[var(--bg-tertiary)] pb-4 flex items-center justify-between">
        {/* Star Icons */}
        <div className="flex gap-0.5">
          {[1, 2, 3, 4, 5].map((star) => (
            <svg
              key={star}
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-[24px] h-[24px] text-yellow-400"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
          ))}
        </div>

        {/* Rating Score */}
        <div className="font-sans font-semibold text-[16px] text-black">
          {averageRating.toFixed(1)} / 5
        </div>
      </div>

      {/* Rating Breakdown */}
      <div className="flex flex-col gap-2">
        {[5, 4, 3, 2, 1].map((starCount) => {
          const count = ratingBreakdown[starCount] || 0;
          return (
            <div key={starCount} className="flex gap-2 items-center">
              {/* Mini Stars */}
              <div className="flex gap-0.5">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg
                    key={star}
                    viewBox="0 0 16 16"
                    fill={star <= starCount ? 'currentColor' : 'none'}
                    stroke="currentColor"
                    strokeWidth={star <= starCount ? 0 : 1}
                    className="w-[16px] h-[16px] text-yellow-400"
                  >
                    <path d="M8 0l2.163 4.382 4.837.703-3.5 3.411.826 4.816L8 11.236l-4.326 2.076.826-4.816-3.5-3.411 4.837-.703L8 0z" />
                  </svg>
                ))}
              </div>

              {/* Count Text */}
              <div className="font-sans font-medium text-[16px] text-text-secondary">
                {count} {getReviewWord(count)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Review Photos Carousel */}
      {reviewPhotos.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {reviewPhotos.map((photo) => (
            <div
              key={photo.id}
              className="flex-shrink-0 w-[60px] h-[60px] rounded-[6px] overflow-hidden bg-bg-light"
            >
              <img
                src={photo.url}
                alt={`Фото от покупателя ${photo.id}`}
                className="w-full h-full object-cover"
              />
            </div>
          ))}
        </div>
      )}

      {/* Individual Reviews */}
      <div className="flex flex-col gap-4">
        {reviews.map((review) => (
          <div key={review.id} className="border-b-2 border-[var(--bg-tertiary)] pb-6 flex gap-4">
            {/* Avatar */}
            <div className="w-[30px] h-[30px] rounded-full bg-[var(--bg-secondary)] flex items-center justify-center flex-shrink-0 overflow-hidden">
              {review.avatar ? (
                <img src={review.avatar} alt={review.author} className="w-full h-full object-cover" />
              ) : (
                <svg viewBox="0 0 30 30" fill="none" className="w-full h-full">
                  <circle cx="15" cy="10" r="5" fill="var(--border-default)" />
                  <path
                    d="M5 25c0-5 5-7.5 10-7.5s10 2.5 10 7.5"
                    fill="var(--border-default)"
                  />
                </svg>
              )}
            </div>

            {/* Review Content */}
            <div className="flex-1 flex flex-col gap-2">
              {/* Author Header */}
              <div className="flex flex-col gap-2">
                {/* Name and Date */}
                <div className="flex gap-2 items-start">
                  <span className="font-sans font-bold text-[14px] text-black">
                    {review.author}
                  </span>
                  <span className="font-sans font-medium text-[14px] text-text-secondary">
                    {review.date}
                  </span>
                </div>

                {/* Rating Stars + Label */}
                <div className="flex gap-2 items-center">
                  <div className="flex gap-0.5">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg
                        key={star}
                        viewBox="0 0 16 16"
                        fill={star <= review.rating ? 'currentColor' : 'none'}
                        stroke="currentColor"
                        strokeWidth={star <= review.rating ? 0 : 1}
                        className="w-[16px] h-[16px] text-yellow-400"
                      >
                        <path d="M8 0l2.163 4.382 4.837.703-3.5 3.411.826 4.816L8 11.236l-4.326 2.076.826-4.816-3.5-3.411 4.837-.703L8 0z" />
                      </svg>
                    ))}
                  </div>
                  <span className="font-sans font-medium text-[14px] text-[var(--text-secondary)]">
                    Отличный товар
                  </span>
                </div>
              </div>

              {/* Review Text */}
              <p className="font-sans font-normal text-[14px] text-black leading-[1.3]">
                {review.text}
              </p>

              {/* Review Photos */}
              {review.photos && review.photos.length > 0 && (
                <div className="flex gap-2 overflow-x-auto scrollbar-hide">
                  {review.photos.map((photo, index) => (
                    <div
                      key={index}
                      className="flex-shrink-0 w-[60px] h-[60px] rounded-[6px] overflow-hidden bg-bg-light"
                    >
                      <img
                        src={photo}
                        alt={`Фото к отзыву ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Actions Row */}
              <div className="flex items-center justify-between">
                {/* Comment Button */}
                <CvetyButton variant="link" size="sm" className="text-[14px] text-[var(--text-secondary)]">
                  Комментировать
                </CvetyButton>

                {/* Like/Dislike Buttons */}
                <div className="flex gap-4">
                  {/* Thumbs Up */}
                  <button
                    onClick={() => handleLike(review.id)}
                    className="flex items-center gap-2"
                  >
                    <svg viewBox="0 0 16 16" fill="none" className="w-[16px] h-[16px]">
                      <path
                        d="M14 6h-3V3.5C11 2.672 10.328 2 9.5 2S8 2.672 8 3.5V6H5.5C4.672 6 4 6.672 4 7.5v5C4 13.328 4.672 14 5.5 14H13c.828 0 1.5-.672 1.5-1.5v-5C14.5 6.672 13.828 6 13 6h1z"
                        stroke="var(--text-secondary)"
                        strokeWidth="1"
                        fill={likedReviews.includes(review.id) ? 'var(--text-secondary)' : 'none'}
                      />
                    </svg>
                    <span className="font-sans font-medium text-[14px] text-[var(--text-secondary)]">
                      {review.likes + (likedReviews.includes(review.id) ? 1 : 0)}
                    </span>
                  </button>

                  {/* Thumbs Down */}
                  <button
                    onClick={() => handleDislike(review.id)}
                    className="flex items-center gap-2"
                  >
                    <svg viewBox="0 0 16 16" fill="none" className="w-[16px] h-[16px]">
                      <path
                        d="M2 10h3v2.5C5 13.328 5.672 14 6.5 14S8 13.328 8 12.5V10h2.5c.828 0 1.5-.672 1.5-1.5v-5C12 2.672 11.328 2 10.5 2H3C2.172 2 1.5 2.672 1.5 3.5v5C1.5 9.328 2.172 10 3 10H2z"
                        stroke="var(--text-secondary)"
                        strokeWidth="1"
                        fill={dislikedReviews.includes(review.id) ? 'var(--text-secondary)' : 'none'}
                      />
                    </svg>
                    <span className="font-sans font-medium text-[14px] text-[var(--text-secondary)]">
                      {review.dislikes + (dislikedReviews.includes(review.id) ? 1 : 0)}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Show More Button */}
      {hasMore && (
        <CvetyButton
          variant="secondary"
          size="md"
          fullWidth
          onClick={onLoadMore}
          className="h-12 font-medium"
        >
          Показать еще отзывы
        </CvetyButton>
      )}
    </div>
  );
}
