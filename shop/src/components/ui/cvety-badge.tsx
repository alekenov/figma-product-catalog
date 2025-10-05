import React from 'react';
import { cn } from './utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'neutral';
  size?: 'sm' | 'default';
}

export const CvetyBadge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center rounded-full';
    
    const variants = {
      default: 'bg-[var(--brand-primary)] text-[var(--text-inverse)]',
      success: 'bg-[var(--brand-success)] text-[var(--text-inverse)]',
      warning: 'bg-[var(--brand-warning)] text-[var(--text-inverse)]',
      error: 'bg-[var(--brand-error)] text-[var(--text-inverse)]',
      neutral: 'bg-[var(--neutral-200)] text-[var(--text-primary)]'
    };
    
    const sizes = {
      sm: 'px-2 py-0.5 text-micro',
      default: 'px-3 py-1 text-label'
    };
    
    return (
      <div
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);

CvetyBadge.displayName = 'CvetyBadge';