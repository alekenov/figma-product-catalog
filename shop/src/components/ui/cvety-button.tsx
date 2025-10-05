import React from 'react';
import { cn } from './utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive';
  size?: 'sm' | 'default' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
}

export const CvetyButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'default', fullWidth = false, loading = false, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg text-button transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] disabled:pointer-events-none disabled:opacity-50';
    
    const variants = {
      primary: 'bg-[var(--brand-primary)] text-[var(--text-inverse)] hover:bg-[var(--brand-primary-dark)] active:bg-[var(--brand-primary-dark)]',
      secondary: 'border-2 border-[var(--brand-primary)] text-[var(--brand-primary)] bg-transparent hover:bg-[var(--brand-primary)] hover:text-[var(--text-inverse)]',
      ghost: 'text-[var(--brand-primary)] hover:bg-[var(--neutral-100)] active:bg-[var(--neutral-200)]',
      destructive: 'bg-[var(--brand-error)] text-[var(--text-inverse)] hover:bg-red-600 active:bg-red-700'
    };
    
    const sizes = {
      sm: 'h-[var(--button-height-sm)] px-4 text-button-small',
      default: 'h-[var(--button-height)] px-6 text-button',
      lg: 'h-[var(--button-height-lg)] px-8 text-subtitle'
    };
    
    return (
      <button
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="mr-2 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

CvetyButton.displayName = 'CvetyButton';