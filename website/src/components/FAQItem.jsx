import React, { useState } from 'react';

// Иконка стрелки вниз
const ArrowDownIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path
      d="M8 12L16 20L24 12"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

// Иконка стрелки вверх
const ArrowUpIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path
      d="M8 20L16 12L24 20"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/**
 * FAQItem - один элемент аккордеона FAQ
 *
 * @param {string} question - Вопрос
 * @param {string} answer - Ответ
 * @param {boolean} defaultOpen - Открыт ли по умолчанию
 */
export default function FAQItem({ question, answer, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="box-border content-stretch flex flex-col items-start px-0 py-2 relative shrink-0 w-full border-b border-text-grey-dark">
      {/* Заголовок с вопросом и кнопкой */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="content-stretch flex gap-10 items-start relative shrink-0 w-full text-left"
      >
        {/* Вопрос */}
        <div
          className={`flex-1 font-sans font-semibold text-body-1 tracking-[0.1px] ${
            isOpen ? 'text-text-black' : 'text-text-grey-dark'
          }`}
        >
          {question}
        </div>

        {/* Иконка */}
        <div className="overflow-clip relative shrink-0 size-8">
          {isOpen ? <ArrowUpIcon /> : <ArrowDownIcon />}
        </div>
      </button>

      {/* Ответ (показывается только когда открыт) */}
      {isOpen && (
        <div className="content-stretch flex flex-col gap-4 items-start mt-4 relative shrink-0 w-full">
          <div className="font-sans font-normal text-body-1 text-text-black tracking-[-0.4px]">
            {answer}
          </div>
        </div>
      )}
    </div>
  );
}