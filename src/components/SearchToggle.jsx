import React, { useState, useRef, useEffect } from 'react';

/**
 * Smart Adaptive Search Component - Вариант 1
 * Состояния: collapsed (иконка) ↔ expanded (поле ввода)
 *
 * @param {string} searchQuery - Current search value
 * @param {function} onSearchChange - Search value change handler
 * @param {string} placeholder - Search placeholder text
 * @param {boolean} enabled - Whether search is enabled (has data to search)
 * @param {boolean} forceExpanded - Force expanded state (optional)
 */
const SearchToggle = ({
  searchQuery,
  onSearchChange,
  placeholder = "Поиск",
  enabled = true,
  forceExpanded = false
}) => {
  const [isExpanded, setIsExpanded] = useState(forceExpanded || !!searchQuery);
  const inputRef = useRef(null);
  const containerRef = useRef(null);

  // Handle click outside to collapse
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target) &&
        !searchQuery.trim() &&
        !forceExpanded
      ) {
        setIsExpanded(false);
      }
    };

    if (isExpanded) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isExpanded, searchQuery, forceExpanded]);

  // Auto-focus when expanded
  useEffect(() => {
    if (isExpanded && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isExpanded]);

  // Force expanded if there's a search query
  useEffect(() => {
    if (searchQuery.trim() || forceExpanded) {
      setIsExpanded(true);
    }
  }, [searchQuery, forceExpanded]);

  const handleIconClick = () => {
    if (!enabled) return;
    setIsExpanded(true);
  };

  const handleInputChange = (e) => {
    onSearchChange(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && !searchQuery.trim() && !forceExpanded) {
      setIsExpanded(false);
      inputRef.current?.blur();
    }
  };

  // Collapsed state - just icon in header
  if (!isExpanded) {
    return (
      <button
        onClick={handleIconClick}
        disabled={!enabled}
        className={`w-6 h-6 flex items-center justify-center ${
          enabled
            ? 'cursor-pointer hover:bg-gray-100 rounded'
            : 'cursor-not-allowed opacity-50'
        }`}
        aria-label="Открыть поиск"
      >
        <svg
          className={`w-6 h-6 ${enabled ? 'stroke-black' : 'stroke-gray-disabled'}`}
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle cx="11" cy="11" r="8" strokeWidth="2"/>
          <path strokeWidth="2" strokeLinecap="round" d="M21 21l-4.35-4.35"/>
        </svg>
      </button>
    );
  }

  // Expanded state - full search input
  return (
    <div ref={containerRef} className="px-4 mt-6">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          className="w-full px-4 py-3 bg-gray-input-alt rounded-lg text-base font-['Open_Sans'] placeholder-gray-placeholder outline-none pr-10 transition-all duration-200"
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

          {/* Collapse button */}
          {!forceExpanded && (
            <button
              onClick={() => {
                if (!searchQuery.trim()) {
                  setIsExpanded(false);
                }
              }}
              className="w-4 h-4 flex items-center justify-center hover:bg-gray-200 rounded-full"
              aria-label="Свернуть поиск"
            >
              <svg className="w-3 h-3 stroke-gray-placeholder" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchToggle;