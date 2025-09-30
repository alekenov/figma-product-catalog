import React from 'react';

/**
 * ProductTag - бейдж для карточки товара (например, "Популярное", "Новинка", "Скидка")
 *
 * @param {string} text - Текст тега
 * @param {string} variant - Вариант стиля ('popular', 'new', 'discount')
 */
export default function ProductTag({ text = 'Популярное', variant = 'popular' }) {
  const variants = {
    popular: 'bg-pink text-white',
    new: 'bg-green-success text-white',
    discount: 'bg-yellow-400 text-black'
  };

  return (
    <div className={`${variants[variant] || variants.popular} inline-flex items-center px-2 py-1.5 rounded-full`}>
      <span className="font-sans font-normal text-body-2 leading-none">
        {text}
      </span>
    </div>
  );
}