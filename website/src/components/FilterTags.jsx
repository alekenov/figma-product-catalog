import React, { useState } from 'react';

/**
 * FilterTag - отдельный тег фильтра
 */
function FilterTag({ label, icon, isActive, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        box-border content-stretch flex gap-1 h-8 items-center justify-center px-3 py-1
        relative rounded-full shrink-0 transition-colors
        ${isActive
          ? 'bg-pink text-text-white'
          : 'bg-bg-light text-text-black hover:bg-bg-extra-light'
        }
      `}
    >
      {icon && (
        <div className="relative shrink-0 size-[14px]">
          {icon}
        </div>
      )}
      <div className="font-sans font-normal leading-normal text-body-1 whitespace-nowrap">
        {label}
      </div>
    </button>
  );
}

/**
 * FilterTags - горизонтальный скролл с тегами фильтров
 *
 * @param {Array} tags - Массив тегов [{id, label, icon?}]
 * @param {Array} activeTags - Массив ID активных тегов
 * @param {function} onTagClick - Колбэк при клике на тег (id)
 */
export default function FilterTags({ tags = [], activeTags = [], onTagClick }) {
  return (
    <div className="content-stretch flex flex-col gap-2 items-start relative w-full overflow-x-auto">
      {/* Row 1 */}
      <div className="content-stretch flex gap-2 items-start relative shrink-0">
        {tags.slice(0, 3).map((tag) => (
          <FilterTag
            key={tag.id}
            label={tag.label}
            icon={tag.icon}
            isActive={activeTags.includes(tag.id)}
            onClick={() => onTagClick?.(tag.id)}
          />
        ))}
      </div>

      {/* Row 2 */}
      {tags.length > 3 && (
        <div className="content-stretch flex gap-2 items-start relative shrink-0">
          {tags.slice(3, 6).map((tag) => (
            <FilterTag
              key={tag.id}
              label={tag.label}
              icon={tag.icon}
              isActive={activeTags.includes(tag.id)}
              onClick={() => onTagClick?.(tag.id)}
            />
          ))}
        </div>
      )}

      {/* Row 3 */}
      {tags.length > 6 && (
        <div className="content-stretch flex gap-2 items-start relative shrink-0">
          {tags.slice(6).map((tag) => (
            <FilterTag
              key={tag.id}
              label={tag.label}
              icon={tag.icon}
              isActive={activeTags.includes(tag.id)}
              onClick={() => onTagClick?.(tag.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Экспортируем иконки для тегов
export const FilterIcons = {
  Lightning: () => (
    <svg width="8" height="14" viewBox="0 0 8 14" fill="none">
      <path
        d="M7 1L1 8H4L1 13"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  Star: () => (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path
        d="M7 1L8.5 5.5H13L9.5 8.5L11 13L7 10L3 13L4.5 8.5L1 5.5H5.5L7 1Z"
        fill="currentColor"
      />
    </svg>
  ),
};