import React from 'react';

/**
 * PillButton - Exact Figma pill-shaped button (38px height)
 * Dimensions from Figma: 38px height, 13px horizontal padding, 9.5px vertical padding
 *
 * @param {boolean} selected - Whether the pill is selected
 * @param {function} onClick - Click handler
 * @param {ReactNode} children - Button content
 * @param {boolean} hasNotification - Whether to show red notification dot (16x16px)
 * @param {string} className - Additional CSS classes
 */
export default function PillButton({
  selected = false,
  onClick,
  children,
  hasNotification = false,
  className = ''
}) {
  return (
    <button
      onClick={onClick}
      style={{
        height: '38px',
        paddingLeft: '13px',
        paddingRight: '13px',
        paddingTop: '9.5px',
        paddingBottom: '9.5px',
        fontSize: '14px',
        lineHeight: '20px',
      }}
      className={`
        relative
        flex-shrink-0
        rounded-full
        font-sans font-normal
        transition-all duration-200
        ${selected
          ? 'bg-[#FF6666] text-white border-[1px] border-[#FF6666]'
          : 'bg-white text-[#000000] border-[1px] border-[#ECECEC] hover:border-[#FF6666]'
        }
        ${className}
      `}
    >
      {children}

      {/* Notification Dot - 16x16px positioned at top-right */}
      {hasNotification && (
        <span
          className="absolute rounded-full bg-[#FF0000]"
          style={{
            width: '10px',
            height: '10px',
            top: '3px',
            right: '3px'
          }}
        />
      )}
    </button>
  );
}
