import React from 'react';
import { cn } from './utils';

/**
 * CvetyQuantityControl - Quantity selector component
 *
 * Aligned to reference implementation:
 * - Background: neutral-100 (no border)
 * - Border radius: 8px (--radius-md)
 * - Stroke width: 2px for icons
 * - Optional trash icon when value === 1
 *
 * @example
 * <CvetyQuantityControl
 *   value={quantity}
 *   onDecrease={() => setQuantity(q => Math.max(1, q - 1))}
 *   onIncrease={() => setQuantity(q => q + 1)}
 *   showTrashIcon
 * />
 */
export const CvetyQuantityControl = ({
  value,
  onDecrease,
  onIncrease,
  min = 1,
  max = 99,
  className,
  showTrashIcon = false
}) => {
  const canDecrease = value > min;
  const canIncrease = value < max;
  const shouldShowTrash = showTrashIcon && value === 1;

  return (
    <div className={cn(
      'flex items-center gap-4 bg-[var(--neutral-100)] rounded-[var(--radius-md)] px-3 py-2',
      className
    )}>
      <button
        onClick={onDecrease}
        disabled={!canDecrease && !shouldShowTrash}
        className={cn(
          'flex items-center justify-center w-6 h-6 rounded transition-colors',
          (canDecrease || shouldShowTrash)
            ? shouldShowTrash
              ? 'text-[var(--text-secondary)] hover:text-[var(--brand-error)] hover:bg-[var(--neutral-200)]'
              : 'text-[var(--text-primary)] hover:bg-[var(--neutral-200)]'
            : 'text-[var(--text-muted)] cursor-not-allowed'
        )}
        aria-label={shouldShowTrash ? "Удалить товар" : "Уменьшить количество"}
      >
        {shouldShowTrash ? (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M3.33333 8H12.6667"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>

      <span className="font-semibold text-sm min-w-[1.5rem] text-center">
        {value}
      </span>

      <button
        onClick={onIncrease}
        disabled={!canIncrease}
        className={cn(
          'flex items-center justify-center w-6 h-6 rounded transition-colors',
          canIncrease
            ? 'text-[var(--text-primary)] hover:bg-[var(--neutral-200)]'
            : 'text-[var(--text-muted)] cursor-not-allowed'
        )}
        aria-label="Увеличить количество"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M8 3.33333V12.6667"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M3.33333 8H12.6667"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </div>
  );
};

CvetyQuantityControl.displayName = 'CvetyQuantityControl';

export default CvetyQuantityControl;
