import React from 'react';

/**
 * Search Input Component - Rendered below header when search is expanded
 *
 * @param {string} searchQuery - Current search value
 * @param {function} onSearchChange - Search value change handler
 * @param {string} placeholder - Search placeholder text
 * @param {function} onClose - Callback to close the search
 * @param {React.RefObject} inputRef - Reference to the input element
 */
const SearchInput = ({
  searchQuery,
  onSearchChange,
  placeholder = "Поиск",
  onClose,
  inputRef
}) => {
  return (
    <div className="px-4 mt-4">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Escape' && !searchQuery.trim()) {
              onClose && onClose();
            }
          }}
          className="w-full px-4 py-3 bg-gray-input-alt rounded-lg text-base font-sans placeholder-gray-placeholder outline-none pr-12 transition-all duration-200"
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
          {/* Search icon */}
          <svg
            className="w-4 h-4 stroke-gray-placeholder"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle cx="11" cy="11" r="8" strokeWidth="2"/>
            <path strokeWidth="2" strokeLinecap="round" d="M21 21l-4.35-4.35"/>
          </svg>

          {/* Clear button when there's text */}
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="w-4 h-4 flex items-center justify-center hover:bg-gray-200 rounded-full"
              aria-label="Очистить поиск"
            >
              <svg className="w-3 h-3 stroke-gray-placeholder" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchInput;