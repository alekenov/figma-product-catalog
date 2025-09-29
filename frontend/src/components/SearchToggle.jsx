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
 * @param {boolean} isExpanded - External control of expanded state
 * @param {function} onExpandedChange - Callback when expanded state changes
 */
const SearchToggle = ({
  searchQuery,
  onSearchChange,
  placeholder = "Поиск",
  enabled = true,
  forceExpanded = false,
  isExpanded: externalIsExpanded,
  onExpandedChange
}) => {
  const [internalIsExpanded, setInternalIsExpanded] = useState(forceExpanded || !!searchQuery);
  const isExpanded = externalIsExpanded !== undefined ? externalIsExpanded : internalIsExpanded;
  const setIsExpanded = (value) => {
    if (onExpandedChange) {
      onExpandedChange(value);
    } else {
      setInternalIsExpanded(value);
    }
  };

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
    setIsExpanded(!isExpanded);
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

  // Always render the icon button in the header
  const iconButton = (
    <button
      onClick={handleIconClick}
      disabled={!enabled}
      className={`w-6 h-6 flex items-center justify-center ${
        enabled
          ? 'cursor-pointer hover:bg-gray-100 rounded'
          : 'cursor-not-allowed opacity-50'
      }`}
      aria-label={isExpanded ? "Свернуть поиск" : "Открыть поиск"}
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

  return iconButton;
};

export default SearchToggle;