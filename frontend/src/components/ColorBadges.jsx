import React from 'react';
import { getColorHex, needsBorder } from '../utils/colors';

/**
 * ColorBadges component
 * Displays product colors as small circular badges
 *
 * @param {string[]} colors - Array of color names
 * @param {number} maxVisible - Maximum number of colors to show (default 3)
 * @param {string} size - Size variant ('sm' | 'md')
 */
const ColorBadges = ({ colors, maxVisible = 3, size = 'sm' }) => {
  if (!colors || colors.length === 0) return null;

  const visibleColors = colors.slice(0, maxVisible);
  const remainingCount = colors.length - maxVisible;

  const sizeStyles = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4'
  };

  return (
    <div className="flex items-center gap-1 mt-1">
      {visibleColors.map((colorName, index) => (
        <div
          key={index}
          className={`
            ${sizeStyles[size]}
            rounded-full
            flex-shrink-0
          `}
          style={{
            backgroundColor: getColorHex(colorName),
            border: needsBorder(colorName) ? '1px solid #E0E0E0' : 'none'
          }}
          title={colorName}
        />
      ))}
      {remainingCount > 0 && (
        <span className="text-xs font-['Open_Sans'] text-gray-disabled ml-0.5">
          +{remainingCount}
        </span>
      )}
    </div>
  );
};

export default ColorBadges;
