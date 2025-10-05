import React from 'react';

/**
 * PlatformReviewCard - карточка отзыва о платформе с интерактивными элементами
 *
 * Дизайн из Figma: 352x297px (expanded) или 352x239px (collapsed) карточка
 *
 * @param {string} authorName - Имя автора ("Елена М.")
 * @param {string} date - Дата отзыва ("20.03.2023")
 * @param {number} rating - Рейтинг (1-5)
 * @param {string} reviewTitle - Заголовок отзыва ("Отличная платформа")
 * @param {string} text - Полный текст отзыва
 * @param {boolean} isExpanded - Показывать ли полный текст
 * @param {boolean} hasReadMore - Есть ли кнопка "Читать полностью"
 * @param {number} likesCount - Количество лайков
 * @param {number} dislikesCount - Количество дизлайков
 * @param {function} onToggleExpand - Колбэк при клике "Читать полностью"
 * @param {function} onLike - Колбэк при клике на лайк
 * @param {function} onDislike - Колбэк при клике на дизлайк
 * @param {function} onReply - Колбэк при клике "Ответить"
 */
export default function PlatformReviewCard({
  authorName,
  date,
  rating,
  reviewTitle,
  text,
  isExpanded = false,
  hasReadMore = false,
  likesCount = 0,
  dislikesCount = 0,
  onToggleExpand,
  onLike,
  onDislike,
  onReply
}) {
  // Обрезаем текст для неразвернутого состояния (примерно 130px = ~5 строк)
  const displayText = !isExpanded && hasReadMore && text.length > 150
    ? text.substring(0, 150) + '...'
    : text;

  return (
    <div className="bg-white box-border flex flex-col pt-[16px] px-[16px] pb-0 rounded-[8px] w-full">
      <div className="flex flex-col gap-[12px] w-full">
        {/* Header: Имя, дата, рейтинг, заголовок */}
        <div className="flex flex-col gap-[4px] w-full">
          {/* Имя + Дата */}
          <div className="flex gap-[8px] items-center h-[24px] w-full">
            <span className="font-['Open_Sans'] font-normal text-[16px] leading-[24px] text-[#212121]">
              {authorName}
            </span>
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
              {date}
            </span>
          </div>

          {/* Рейтинг + Заголовок отзыва */}
          <div className="flex gap-[8px] items-center h-[21px] w-full">
            {/* Звездочки */}
            <div className="flex gap-[4px] items-center h-[16px]">
              {[...Array(5)].map((_, index) => (
                <svg
                  key={index}
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  className="shrink-0"
                >
                  <path
                    d="M8 1.33333L9.88 5.14667L14 5.74667L11 8.66667L11.72 12.7733L8 10.78L4.28 12.7733L5 8.66667L2 5.74667L6.12 5.14667L8 1.33333Z"
                    fill={index < rating ? '#FFB800' : '#E0E0E0'}
                  />
                </svg>
              ))}
            </div>

            {/* Заголовок отзыва */}
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
              {reviewTitle}
            </span>
          </div>
        </div>

        {/* Текст отзыва */}
        <div className="w-full">
          <p className="font-['Open_Sans'] font-normal text-[16px] leading-[26px] text-[#212121] whitespace-pre-wrap">
            {displayText}
          </p>

          {/* Кнопка "Читать полностью" */}
          {hasReadMore && !isExpanded && (
            <button
              onClick={onToggleExpand}
              className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#ff6666] mt-[10px] hover:underline"
            >
              Читать полностью
            </button>
          )}
        </div>

        {/* Действия: Лайк, Дизлайк, Ответить */}
        <div className="border-t border-[#eeeeee] flex gap-[16px] items-center h-[30px] pt-[1px] w-full">
          {/* Лайк */}
          <button
            onClick={onLike}
            className="flex gap-[4px] items-center h-[21px] hover:opacity-70 transition-opacity"
          >
            {/* Thumb up icon */}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="shrink-0">
              <path
                d="M3.5 13.125H2.625C2.19402 13.125 1.78075 12.954 1.47595 12.649C1.17116 12.344 1 11.931 1 11.5V7.875C1 7.44402 1.17116 7.03075 1.47595 6.72595C1.78075 6.42116 2.19402 6.25 2.625 6.25H3.5M7.875 5.375V2.625C7.875 2.19402 7.70384 1.78075 7.39905 1.47595C7.09425 1.17116 6.68098 1 6.25 1L3.5 6.25V13.125H10.8188C11.2012 13.1283 11.5697 12.9862 11.8503 12.7275C12.131 12.4687 12.3029 12.1127 12.3313 11.7325L12.9063 6.4825C12.9222 6.30512 12.9015 6.12651 12.8456 5.95759C12.7897 5.78868 12.6997 5.63317 12.5814 5.50052C12.463 5.36787 12.3188 5.26094 12.1578 5.18624C11.9968 5.11153 11.8224 5.07065 11.6438 5.0625H7.875Z"
                stroke="#8F8F8F"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
              {likesCount}
            </span>
          </button>

          {/* Дизлайк */}
          <button
            onClick={onDislike}
            className="flex gap-[4px] items-center h-[21px] hover:opacity-70 transition-opacity"
          >
            {/* Thumb down icon */}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="shrink-0">
              <path
                d="M10.5 0.875H11.375C11.806 0.875 12.2192 1.04616 12.524 1.35095C12.8288 1.65575 13 2.06902 13 2.5V6.125C13 6.55598 12.8288 6.96925 12.524 7.27405C12.2192 7.57884 11.806 7.75 11.375 7.75H10.5M6.125 8.625V11.375C6.125 11.806 6.29616 12.2192 6.60095 12.524C6.90575 12.8288 7.31902 13 7.75 13L10.5 7.75V0.875H3.18125C2.79876 0.871701 2.43031 1.01385 2.14966 1.27247C1.869 1.53109 1.69714 1.88726 1.66875 2.2675L1.09375 7.5175C1.07775 7.69488 1.09852 7.87349 1.15444 8.04241C1.21035 8.21132 1.30031 8.36683 1.41865 8.49948C1.53698 8.63213 1.68118 8.73906 1.84219 8.81376C2.00321 8.88847 2.17761 8.92935 2.35625 8.9375H6.125Z"
                stroke="#8F8F8F"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
              {dislikesCount}
            </span>
          </button>

          {/* Ответить */}
          <button
            onClick={onReply}
            className="flex gap-[4px] items-center h-[21px] hover:opacity-70 transition-opacity"
          >
            {/* Reply icon */}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="shrink-0">
              <path
                d="M12.25 6.41667C12.25 9.59167 9.04167 12.25 5.25 12.25C4.46467 12.2516 3.68489 12.1177 2.94583 11.855C2.74689 11.7888 2.53219 11.7812 2.32861 11.8333C1.82733 11.9617 1.19833 12.1237 0.875 12.25C1.00267 11.9267 1.16467 11.2977 1.29233 10.7964C1.34438 10.5928 1.33686 10.3781 1.27067 10.1792C1.00796 9.44011 0.874161 8.66033 0.875833 7.875C0.875833 4.37917 4.20833 1.75 7.70417 1.75"
                stroke="#8F8F8F"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M9.625 1.75V5.25M9.625 5.25L11.375 3.5M9.625 5.25L7.875 3.5"
                stroke="#8F8F8F"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="font-['Open_Sans'] font-normal text-[14px] leading-[21px] text-[#8f8f8f]">
              Ответить
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
