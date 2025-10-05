import React from 'react';
import { cn } from './utils';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
  helperText?: string;
  label?: string;
}

export const CvetyTextarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, helperText, label, ...props }, ref) => {
    const textareaId = React.useId();
    
    return (
      <div className="space-y-2">
        {label && (
          <label 
            htmlFor={textareaId}
            className="block text-label text-[var(--text-primary)]"
          >
            {label}
          </label>
        )}
        <textarea
          id={textareaId}
          className={cn(
            'flex min-h-[80px] w-full rounded-[var(--radius-md)] border bg-[var(--input-background)] px-3 py-2 text-body ring-offset-background placeholder:text-[var(--text-muted)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none',
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

CvetyTextarea.displayName = 'CvetyTextarea';