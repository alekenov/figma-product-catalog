import React from 'react';

/**
 * Heart Icon - для кнопки избранного
 * @param {boolean} filled - заполненное сердце или контур
 * @param {string} className - дополнительные CSS классы
 */
export function HeartIcon({ filled = false, className = "w-6 h-6" }) {
  if (filled) {
    return (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.04L12 21.35Z"
          fill="var(--brand-primary)"
        />
      </svg>
    );
  }

  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.04L12 21.35Z"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
      />
    </svg>
  );
}

/**
 * Plus Icon - для кнопки добавления в корзину
 * @param {boolean} active - активное состояние (розовый фон)
 * @param {string} className - дополнительные CSS классы
 */
export function PlusIcon({ active = false, className = "w-[13px] h-[13px]" }) {
  return (
    <svg className={className} viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M6.5 1V12M1 6.5H12"
        stroke={active ? "white" : "currentColor"}
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

/**
 * Star Icon - для рейтинга
 * @param {boolean} filled - заполненная звезда или контур
 * @param {string} className - дополнительные CSS классы
 */
export function StarIcon({ filled = true, className = "w-[9.375px] h-[9.375px]" }) {
  if (filled) {
    return (
      <svg className={className} viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M5 0.833L6.125 3.667L9.167 4.083L7.083 6.083L7.583 9.167L5 7.75L2.417 9.167L2.917 6.083L0.833 4.083L3.875 3.667L5 0.833Z"
          fill="var(--brand-primary)"
        />
      </svg>
    );
  }

  return (
    <svg className={className} viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M5 0.833L6.125 3.667L9.167 4.083L7.083 6.083L7.583 9.167L5 7.75L2.417 9.167L2.917 6.083L0.833 4.083L3.875 3.667L5 0.833Z"
        stroke="var(--brand-primary)"
        strokeWidth="0.8"
        fill="none"
      />
    </svg>
  );
}

/**
 * Truck Icon - для информации о доставке
 * @param {string} className - дополнительные CSS классы
 */
export function TruckIcon({ className = "w-[9.375px] h-[9.375px]" }) {
  return (
    <svg className={className} viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M6.667 1.667H0.833V6.667H6.667V1.667Z"
        stroke="currentColor"
        strokeWidth="0.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6.667 3.333H8.333L9.167 4.167V6.667H6.667V3.333Z"
        stroke="currentColor"
        strokeWidth="0.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M2.5 8.333C3.05228 8.333 3.5 7.88529 3.5 7.333C3.5 6.78072 3.05228 6.333 2.5 6.333C1.94772 6.333 1.5 6.78072 1.5 7.333C1.5 7.88529 1.94772 8.333 2.5 8.333Z"
        stroke="currentColor"
        strokeWidth="0.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7.5 8.333C8.05228 8.333 8.5 7.88529 8.5 7.333C8.5 6.78072 8.05228 6.333 7.5 6.333C6.94772 6.333 6.5 6.78072 6.5 7.333C6.5 7.88529 6.94772 8.333 7.5 8.333Z"
        stroke="currentColor"
        strokeWidth="0.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}