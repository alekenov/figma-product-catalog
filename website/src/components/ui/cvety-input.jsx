import React from 'react';
import { cn } from './utils';

/**
 * CvetyInput - Input field component for forms
 *
 * Aligned to reference implementation:
 * - Height: 48px (h-12)
 * - Border radius: 8px (--radius-md)
 * - Background: neutral-100 (--input-background)
 * - Border: 1px solid (--border)
 *
 * @example
 * <CvetyInput
 *   label="Email"
 *   placeholder="Введите email..."
 *   error={true}
 *   helperText="Неверный формат email"
 * />
 */
export const CvetyInput = React.forwardRef(
  ({ className, type, error, helperText, label, ...props }, ref) => {
    const inputId = React.useId();

    return (
      <div className="space-y-2">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-[var(--text-primary)]"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          className={cn(
            'flex h-12 w-full rounded-[var(--radius-md)] border bg-[var(--input-background)] px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-[var(--text-muted)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            error
              ? 'border-[var(--brand-error)] focus-visible:ring-[var(--brand-error)]'
              : 'border-[var(--border)]',
            className
          )}
          ref={ref}
          {...props}
        />
        {helperText && (
          <p className={cn(
            'text-sm',
            error ? 'text-[var(--brand-error)]' : 'text-[var(--text-secondary)]'
          )}>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

CvetyInput.displayName = 'CvetyInput';

export default CvetyInput;
