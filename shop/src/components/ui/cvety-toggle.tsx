import React from 'react';
import { cn } from './utils';

interface ToggleProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
}

export const CvetyToggle: React.FC<ToggleProps> = ({
  checked,
  onCheckedChange,
  label,
  disabled = false,
  className
}) => {
  return (
    <label className={cn('flex items-center gap-3 cursor-pointer', disabled && 'cursor-not-allowed opacity-50', className)}>
      <div 
        className={cn(
          'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
          checked ? 'bg-[var(--brand-success)]' : 'bg-[var(--neutral-300)]'
        )}
        onClick={() => !disabled && onCheckedChange(!checked)}
      >
        <div
          className={cn(
            'inline-block h-5 w-5 transform rounded-full bg-white transition-transform',
            checked ? 'translate-x-5' : 'translate-x-0.5'
          )}
        />
      </div>
      {label && (
        <span className="font-medium text-[var(--text-primary)]">
          {label}
        </span>
      )}
    </label>
  );
};

CvetyToggle.displayName = 'CvetyToggle';