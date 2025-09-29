import React from 'react';
import ReviewCard from './ReviewCard';

// Иконка звезды для общего рейтинга
const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path
      d="M8 1L9.5 6H14.5L10.5 9.5L12 14.5L8 11L4 14.5L5.5 9.5L1.5 6H6.5L8 1Z"
      fill="#FFB800"
    />
  </svg>
);

// Mock данные для отзывов
const mockReviews = [
  {
    id: 1,
    name: 'Alekenov C.',
    rating: 5,
    date: '15.03.2023',
    text: 'Один из лучших цветочных магазинов в городе..'
  },
  {
    id: 2,
    name: 'Alekenov C.',
    rating: 5,
    date: '15.03.2023',
    text: 'Хороший букет, вовремя доставили'
  },
  {
    id: 3,
    name: 'Alekenov C.',
    rating: 5,
    date: '15.03.2023',
    text: 'Хороший букет, вовремя доставили'
  }
];

/**
 * ReviewsSection - секция отзывов с общим рейтингом
 *
 * @param {function} onShowAll - Колбэк при клике на "Смотреть все"
 */
export default function ReviewsSection({ onShowAll }) {
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
          {/* Рейтинг 4.6 */}
          <div className="content-stretch flex gap-1 items-center relative shrink-0">
            <div className="size-4">
              <StarIcon />
            </div>
            <div className="font-sans font-normal text-field-title text-text-black">
              4.6
            </div>
          </div>

          {/* 164 отзыва */}
          <div className="font-sans font-normal text-field-title text-text-black">
            164 отзыва
          </div>

          {/* 210 оценок */}
          <div className="font-sans font-normal text-field-title text-text-black">
            210 оценок
          </div>
        </div>
      </div>

      {/* Горизонтальный скролл с карточками */}
      <div className="content-stretch flex gap-2 items-start overflow-x-auto relative shrink-0 w-full">
        {mockReviews.map(review => (
          <ReviewCard
            key={review.id}
            name={review.name}
            rating={review.rating}
            date={review.date}
            text={review.text}
          />
        ))}
      </div>
    </div>
  );
}