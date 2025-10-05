import React from 'react';
import { cn } from './utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'default' | 'lg';
}

export const CvetyCard = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', padding = 'default', ...props }, ref) => {
    const baseStyles = 'rounded-[var(--radius-lg)] bg-[var(--card)] text-[var(--card-foreground)]';
    
    const variants = {
      default: 'border border-[var(--border)]',
      elevated: 'shadow-lg border border-[var(--border)]',
      outlined: 'border-2 border-[var(--brand-primary)]'
    };
    
    const paddings = {
      none: '',
      sm: 'p-3',
      default: 'p-[var(--card-padding)]',
      lg: 'p-6'
    };
    
    return (
      <div
        ref={ref}
        className={cn(baseStyles, variants[variant], paddings[padding], className)}
        {...props}
      />
    );
  }
);

CvetyCard.displayName = 'CvetyCard';

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CvetyCardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5', className)} {...props} />
  )
);

CvetyCardHeader.displayName = 'CvetyCardHeader';

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export const CvetyCardTitle = React.forwardRef<HTMLParagraphElement, CardTitleProps>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('font-semibold leading-none tracking-tight', className)} {...props} />
  )
);

CvetyCardTitle.displayName = 'CvetyCardTitle';

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

export const CvetyCardDescription = React.forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-[var(--text-secondary)]', className)} {...props} />
  )
);

CvetyCardDescription.displayName = 'CvetyCardDescription';

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CvetyCardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('', className)} {...props} />
  )
);

CvetyCardContent.displayName = 'CvetyCardContent';

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CvetyCardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center pt-4', className)} {...props} />
  )
);

CvetyCardFooter.displayName = 'CvetyCardFooter';