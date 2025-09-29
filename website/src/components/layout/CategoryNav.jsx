import React, { useState } from 'react';

function Category({ text, isActive = false, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        box-border content-stretch cursor-pointer flex flex-col gap-2 items-center justify-center
        pb-3 pt-2 px-3 relative shrink-0
        transition-all duration-200
        ${isActive ? 'border-b-2 border-pink' : 'border-b-2 border-transparent hover:border-border-grey-light'}
      `}
    >
      <div className={`
        font-sans font-semibold leading-[1.4] relative shrink-0
        text-body-2 whitespace-nowrap
        ${isActive ? 'text-text-black' : 'text-text-grey-dark hover:text-text-black'}
      `}>
        {text}
      </div>
    </button>
  );
}

export default function CategoryNav() {
  const categories = [
    { id: 1, text: "Букеты" },
    { id: 2, text: "Шары" },
    { id: 3, text: "Торты" },
    { id: 4, text: "Подарки" },
    { id: 5, text: "Фрукты" },
    { id: 6, text: "Игрушки" },
    { id: 7, text: "В горшке" },
    { id: 8, text: "Бельё" },
    { id: 9, text: "Корзины" }
  ];

  const [activeCategory, setActiveCategory] = useState(1);

  return (
    <div className="bg-bg-white content-stretch flex items-start overflow-x-auto relative w-full border-b border-border-grey-light">
      <div className="content-stretch flex items-start relative shrink-0">
        {categories.map((category) => (
          <Category
            key={category.id}
            text={category.text}
            isActive={activeCategory === category.id}
            onClick={() => setActiveCategory(category.id)}
          />
        ))}
      </div>
    </div>
  );
}