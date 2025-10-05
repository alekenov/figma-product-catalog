import React from 'react';

// System icons following design system specifications
const ShopIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
    <path
      strokeWidth="1.5"
      d="M17 18H3v-9.5A1.5 1.5 0 014.5 7h11A1.5 1.5 0 0117 8.5V18z"
    />
    <path
      strokeWidth="1.5"
      d="M7 7V4a1 1 0 011-1h4a1 1 0 011 1v3"
    />
  </svg>
);

const DocumentIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
    <path
      strokeWidth="1.5"
      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
    />
  </svg>
);

const FilterIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
    <path
      strokeWidth="1.5"
      d="M4 3h12l-2 6H6L4 3zM6 9v9M14 9v9M10 9v5"
    />
  </svg>
);

/**
 * Unified FilterHeader component following Figma design system
 * @param {string} type - Icon type ('shop' | 'orders')
 * @param {string} label - Left side label text
 * @param {function} onFiltersClick - Filter button click handler
 */
const FilterHeader = ({
  type = "shop",
  label,
  onFiltersClick
}) => {
  const IconComponent = type === "orders" ? DocumentIcon : ShopIcon;

  return (
    <div className="flex items-center justify-end px-4 mt-6">
      <button
        onClick={onFiltersClick}
        className="flex items-center gap-1 text-sm font-['Open_Sans'] text-black"
      >
        <span>Фильтры</span>
        <FilterIcon />
      </button>
    </div>
  );
};

export default FilterHeader;