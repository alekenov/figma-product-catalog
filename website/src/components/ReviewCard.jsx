import React from 'react';

// Иконка звезды для рейтинга
const StarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path
      d="M7 1L8.5 5.5H13L9.5 8.5L11 13L7 10L3 13L4.5 8.5L1 5.5H5.5L7 1Z"
      fill="var(--brand-warning)"
    />
  </svg>
);

/**
 * ReviewCard - карточка отзыва
 *
 * @param {string} name - Имя автора отзыва
 * @param {number} rating - Рейтинг (1-5)
 * @param {string} date - Дата отзыва
 * @param {string} text - Текст отзыва
 */
export default function ReviewCard({ name, rating = 5, date, text }) {
  return (
    <div className="bg-bg-light box-border content-stretch flex flex-col gap-2 items-start p-4 rounded-md shrink-0 w-[250px]">
      {/* Заголовок: имя + рейтинг + дата */}
      <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0">
        {/* Имя */}
        <div className="font-sans font-normal text-body-1 text-text-black">
          {name}
        </div>

        {/* Рейтинг + дата */}
        <div className="content-stretch flex gap-2 items-center relative shrink-0">
          {/* Звёзды */}
          <div className="flex gap-1 items-center">
            {[...Array(rating)].map((_, index) => (
              <div key={index} className="size-[14px]">
                <StarIcon />
              </div>
            ))}
          </div>

          {/* Дата */}
          <div className="font-sans font-normal text-field-title text-text-grey-dark">
            {date}
          </div>
        </div>
      </div>

      {/* Текст отзыва */}
      <div className="font-sans font-normal text-body-1 text-text-black">
        {text}
      </div>
    </div>
  );
}