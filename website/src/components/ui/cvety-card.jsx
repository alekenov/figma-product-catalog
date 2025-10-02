import React from 'react';
import { cn } from './utils';

/**
 * CvetyCard - Card component for content containers
 *
 * Aligned to reference implementation:
 * - Border radius: 12px (--radius-lg)
 * - Default padding: 16px (--card-padding)
 * - Variants: default (border), elevated (shadow), outlined (brand border)
 *
 * @example
 * <CvetyCard variant="elevated" padding="default">
 *   <CvetyCardHeader>
 *     <CvetyCardTitle>Card Title</CvetyCardTitle>
 *     <CvetyCardDescription>Description text</CvetyCardDescription>
 *   </CvetyCardHeader>
 *   <CvetyCardContent>
 *     Card content goes here
 *   </CvetyCardContent>
 *   <CvetyCardFooter>
 *     Footer actions
 *   </CvetyCardFooter>
 * </CvetyCard>
 */
export const CvetyCard = React.forwardRef(
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

export const CvetyCardHeader = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5', className)} {...props} />
  )
);

CvetyCardHeader.displayName = 'CvetyCardHeader';

export const CvetyCardTitle = React.forwardRef(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('font-semibold leading-none tracking-tight', className)} {...props} />
  )
);

CvetyCardTitle.displayName = 'CvetyCardTitle';

export const CvetyCardDescription = React.forwardRef(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-[var(--text-secondary)]', className)} {...props} />
  )
);

CvetyCardDescription.displayName = 'CvetyCardDescription';

export const CvetyCardContent = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('', className)} {...props} />
  )
);

CvetyCardContent.displayName = 'CvetyCardContent';

export const CvetyCardFooter = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center pt-4', className)} {...props} />
  )
);

CvetyCardFooter.displayName = 'CvetyCardFooter';

export default CvetyCard;
