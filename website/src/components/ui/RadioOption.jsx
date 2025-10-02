import React from 'react';

/**
 * RadioOption - Exact Figma radio button (172px wide x 73px tall)
 * Dimensions: 172px width, 73px height, 8px padding, 16x16px radio circle
 *
 * @param {string} value - Option value
 * @param {boolean} selected - Whether this option is selected
 * @param {function} onChange - Change handler
 * @param {string} label - Main label text (24px height)
 * @param {string} sublabel - Secondary text (21px height)
 * @param {string} name - Radio group name for accessibility
 */
export default function RadioOption({
  value,
  selected = false,
  onChange,
  label,
  sublabel,
  name = 'radio-group'
}) {
  return (
    <label
      className="flex items-center justify-between cursor-pointer bg-white border-[1px] border-[#ECECEC] rounded-lg"
      style={{
        width: '172px',
        height: '73px',
        padding: '8px'
      }}
    >
      <div className="flex flex-col" style={{ gap: '2px' }}>
        <span
          className="font-sans font-normal text-[#000000]"
          style={{
            fontSize: '14px',
            lineHeight: '24px',
            height: '24px'
          }}
        >
          {label}
        </span>
        <span
          className="font-sans font-normal text-[#8F9F9F]"
          style={{
            fontSize: '12px',
            lineHeight: '21px',
            height: '21px'
          }}
        >
          {sublabel}
        </span>
      </div>

      {/* Custom Radio Button - 16x16px */}
      <div className="relative flex-shrink-0">
        <input
          type="radio"
          name={name}
          value={value}
          checked={selected}
          onChange={() => onChange(value)}
          className="sr-only"
          aria-label={label}
        />
        <div
          className="rounded-full border-[2px] flex items-center justify-center transition-colors"
          style={{
            width: '16px',
            height: '16px',
            borderColor: selected ? '#FF6666' : '#ECECEC'
          }}
        >
          {selected && (
            <div
              className="rounded-full bg-[#FF6666]"
              style={{
                width: '10px',
                height: '10px'
              }}
            />
          )}
        </div>
      </div>
    </label>
  );
}
