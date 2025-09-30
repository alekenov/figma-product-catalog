import React, { useState, useEffect } from 'react';
import ReviewCard from './ReviewCard';
import { fetchCompanyReviews } from '../services/api';

// Иконка звезды для общего рейтинга
const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path
      d="M8 1L9.5 6H14.5L10.5 9.5L12 14.5L8 11L4 14.5L5.5 9.5L1.5 6H6.5L8 1Z"
      fill="var(--brand-warning)"
    />
  </svg>
);

/**
 * ReviewsSection - секция отзывов с общим рейтингом
 *
 * @param {function} onShowAll - Колбэк при клике на "Смотреть все"
 */
export default function ReviewsSection({ onShowAll }) {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({
    total_count: 0,
    average_rating: 0,
    rating_breakdown: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadReviews() {
      try {
        setLoading(true);
        const data = await fetchCompanyReviews(3, 0); // Fetch first 3 reviews for homepage
        setReviews(data.reviews || []);
        setStats(data.stats || { total_count: 0, average_rating: 0, rating_breakdown: {} });
        setError(null);
      } catch (err) {
        console.error('Failed to load reviews:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadReviews();
  }, []);

  // Format date from ISO string to DD.MM.YYYY
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };
  // Calculate total ratings from rating_breakdown
  const totalRatings = Object.values(stats.rating_breakdown || {}).reduce((sum, count) => sum + count, 0);

  if (loading) {
    return (
      <div className="content-stretch flex flex-col gap-4 items-start relative w-full">
        <div className="font-sans font-normal text-body2 text-text-grey-dark">
          Загрузка отзывов...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content-stretch flex flex-col gap-4 items-start relative w-full">
        <div className="font-sans font-normal text-body2 text-text-grey-dark">
          Не удалось загрузить отзывы
        </div>
      </div>
    );
  }

  return (
    <div className="content-stretch flex flex-col gap-4 items-start relative w-full">
      {/* Заголовок и статистика */}
      <div className="content-stretch flex flex-col gap-2 items-start relative shrink-0">
        {/* Заголовок "Отзывы" + "Смотреть все" */}
        <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
          <h2 className="font-sans font-bold text-h2 text-text-black">
            Отзывы
          </h2>
          {onShowAll && (
            <button
              onClick={onShowAll}
              className="font-sans font-normal text-field-title text-text-black hover:text-pink transition-colors"
            >
              Смотреть все
            </button>
          )}
        </div>

        {/* Рейтинг + статистика */}
        <div className="content-stretch flex gap-2 items-center relative shrink-0">
          {/* Средний рейтинг */}
          <div className="content-stretch flex gap-1 items-center relative shrink-0">
            <div className="size-4">
              <StarIcon />
            </div>
            <div className="font-sans font-normal text-field-title text-text-black">
              {stats.average_rating ? stats.average_rating.toFixed(1) : '0.0'}
            </div>
          </div>

          {/* Количество отзывов */}
          <div className="font-sans font-normal text-field-title text-text-black">
            {stats.total_count} {stats.total_count === 1 ? 'отзыв' : stats.total_count < 5 ? 'отзыва' : 'отзывов'}
          </div>

          {/* Количество оценок */}
          <div className="font-sans font-normal text-field-title text-text-black">
            {totalRatings} {totalRatings === 1 ? 'оценка' : totalRatings < 5 ? 'оценки' : 'оценок'}
          </div>
        </div>
      </div>

      {/* Горизонтальный скролл с карточками */}
      <div className="content-stretch flex gap-2 items-start overflow-x-auto relative shrink-0 w-full">
        {reviews.length > 0 ? (
          reviews.map(review => (
            <ReviewCard
              key={review.id}
              name={review.author_name}
              rating={review.rating}
              date={formatDate(review.created_at)}
              text={review.text}
            />
          ))
        ) : (
          <div className="font-sans font-normal text-body2 text-text-grey-dark">
            Пока нет отзывов
          </div>
        )}
      </div>
    </div>
  );
}