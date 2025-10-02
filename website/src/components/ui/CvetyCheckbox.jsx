import React from 'react';
import { cn } from './utils';

/**
 * CvetyCheckbox - Checkbox component for forms
 *
 * Aligned to reference implementation:
 * - Border radius: 6px (checkbox box)
 * - Checkmark color: White on coral background
 * - Label font-weight: 500 (medium)
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
    md: { box: 20, icon: 12 },
    lg: { box: 24, icon: 14 }
  };

  const currentSize = sizes[size] || sizes.md;

  const handleClick = () => {
    if (!disabled && onChange) {
      onChange(!checked);
    }
  };

  return (
    <label
      htmlFor={checkboxId}
      className={cn(
        'inline-flex items-center gap-2',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
        className
      )}
      {...props}
    >
      <button
        id={checkboxId}
        type="button"
        role="checkbox"
        aria-checked={checked}
        aria-invalid={error}
        onClick={handleClick}
        disabled={disabled}
        className={cn(
          'flex items-center justify-center rounded-md flex-shrink-0 transition-colors',
          checked
            ? 'bg-[var(--brand-primary)] border border-[var(--brand-primary)]'
            : error
              ? 'bg-white border border-[var(--brand-error)]'
              : 'bg-white border border-[var(--border)]',
          disabled ? 'cursor-not-allowed' : 'cursor-pointer hover:border-[var(--brand-primary)]'
        )}
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
        <span className={cn(
          'text-sm font-medium text-[var(--text-primary)] select-none',
          disabled ? 'cursor-not-allowed' : 'cursor-pointer'
        )}>
          {label}
        </span>
      )}
    </label>
  );
};

export default CvetyCheckbox;
