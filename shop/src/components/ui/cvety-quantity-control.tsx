import React from 'react';
import { cn } from './utils';
import { Trash2 } from 'lucide-react';

interface QuantityControlProps {
  value: number;
  onDecrease: () => void;
  onIncrease: () => void;
  min?: number;
  max?: number;
  className?: string;
  showTrashIcon?: boolean;
}

export const CvetyQuantityControl: React.FC<QuantityControlProps> = ({
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
          <Trash2 size={14} />
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