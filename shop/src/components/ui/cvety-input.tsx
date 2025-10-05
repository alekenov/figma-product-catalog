import React from 'react';
import { cn } from './utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  helperText?: string;
  label?: string;
}

export const CvetyInput = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, helperText, label, ...props }, ref) => {
    const inputId = React.useId();
    
    return (
      <div className="space-y-2">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-label text-[var(--text-primary)]"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          className={cn(
            'flex h-12 w-full rounded-[var(--radius-md)] border bg-[var(--input-background)] px-3 py-2 text-body ring-offset-background file:border-0 file:bg-transparent file:text-body file:font-normal placeholder:text-[var(--text-muted)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
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
            'text-caption',
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