import React from 'react';

/**
 * CvetyCheckbox Component
 *
 * Checkbox component for the Cvety.kz design system.
 * Supports label, error state, and different sizes.
 *
 * @example
 * <CvetyCheckbox
 *   checked={agreed}
 *   onChange={setAgreed}
 *   label="Согласен с условиями"
 * />
 */

export const CvetyCheckbox = ({
  checked = false,
  onChange,
  label,
  error = false,
  disabled = false,
  size = 'md',
  className = '',
  ...props
}) => {
  const checkboxId = React.useId();

  // Size variants
  const sizes = {
    sm: { box: 16, icon: 10 },
    md: { box: 19, icon: 11 },
    lg: { box: 24, icon: 14 }
  };

  const currentSize = sizes[size] || sizes.md;

  const containerStyles = `
    inline-flex items-center
    gap-2
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
  `;

  const boxStyles = `
    flex items-center justify-center
    rounded-[4px]
    flex-shrink-0
    transition-colors duration-200
    ${checked
      ? 'bg-[var(--brand-primary)]'
      : error
        ? 'bg-white border border-[var(--brand-error)]'
        : 'bg-white border border-[var(--border-default)]'
    }
    ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
  `;

  const labelStyles = `
    text-sm font-normal
    text-[var(--text-primary)]
    ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
    select-none
  `;

  const combinedClassName = `${containerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  const handleClick = () => {
    if (!disabled && onChange) {
      onChange(!checked);
    }
  };

  return (
    <label htmlFor={checkboxId} className={combinedClassName} {...props}>
      <button
        id={checkboxId}
        type="button"
        role="checkbox"
        aria-checked={checked}
        aria-invalid={error}
        onClick={handleClick}
        disabled={disabled}
        className={boxStyles}
        style={{ width: `${currentSize.box}px`, height: `${currentSize.box}px` }}
      >
        {checked && (
          <svg
            viewBox="0 0 16 16"
            fill="none"
            className="text-white"
            style={{ width: `${currentSize.icon}px`, height: `${currentSize.icon}px` }}
          >
            <path
              d="M13.5 4L6 11.5L2.5 8"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>
      {label && (
        <span className={labelStyles}>
          {label}
        </span>
      )}
    </label>
  );
};

export default CvetyCheckbox;
