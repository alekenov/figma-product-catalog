import React from 'react';

/**
 * Unified SearchInput component following Figma design system
 * @param {string} placeholder - Search placeholder text
 * @param {string} value - Current search value
 * @param {function} onChange - Value change handler
 * @param {string} variant - Input background variant ('default' | 'alt')
 */
const SearchInput = ({
  placeholder = "Поиск",
  value,
  onChange,
  variant = "default"
}) => {
  const bgClass = variant === "alt" ? "bg-gray-input-alt" : "bg-gray-input";

  return (
    <div className="px-4 mt-6">
      <div className="relative">
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full px-4 py-3 ${bgClass} rounded-lg text-base font-['Open_Sans'] placeholder-gray-placeholder outline-none pr-10`}
        />
        <svg
          className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
          fill="none"
          stroke="#828282"
          viewBox="0 0 24 24"
        >
          <circle cx="11" cy="11" r="8" strokeWidth="2"/>
          <path strokeWidth="2" strokeLinecap="round" d="M21 21l-4.35-4.35"/>
        </svg>
      </div>
    </div>
  );
};

export default SearchInput;