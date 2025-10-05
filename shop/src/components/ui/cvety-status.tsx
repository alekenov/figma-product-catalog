import React from 'react';
import { cn } from './utils';

interface StatusProps {
  steps: Array<{
    label: string;
    completed: boolean;
  }>;
  className?: string;
}

export const CvetyStatus: React.FC<StatusProps> = ({ steps, className }) => {
  return (
    <div className={cn('w-full', className)}>
      {/* Progress Bar */}
      <div className="flex gap-1 mb-2">
        {steps.map((_, index) => (
          <div
            key={index}
            className={cn(
              'flex-1 h-1.5 rounded-full',
              steps[index].completed 
                ? 'bg-[var(--brand-success)]' 
                : 'bg-[var(--neutral-200)]'
            )}
          />
        ))}
      </div>
      
      {/* Step Labels */}
      <div className="flex justify-between text-xs text-[var(--text-secondary)]">
        {steps.map((step, index) => (
          <span 
            key={index}
            className={cn(
              'text-center',
              step.completed && 'text-[var(--brand-success)]'
            )}
          >
            {step.label}
          </span>
        ))}
      </div>
    </div>
  );
};

CvetyStatus.displayName = 'CvetyStatus';