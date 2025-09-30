import React from 'react';

/**
 * CvetyStatus Component
 *
 * Status indicator for order tracking and multi-step processes in the Cvety.kz design system.
 *
 * @example
 * <CvetyStatus steps={[
 *   { label: 'подтвержден', completed: true },
 *   { label: 'собираем', completed: true },
 *   { label: 'доставляем', completed: false }
 * ]} />
 */

export const CvetyStatus = ({
  steps = [],
  className = '',
  ...props
}) => {
  const containerStyles = `
    flex items-center justify-between
    w-full
  `;

  const stepContainerStyles = `
    flex flex-col items-center
    flex-1
  `;

  const stepDotStyles = (completed) => `
    w-8 h-8
    rounded-full
    flex items-center justify-center
    border-2
    transition-colors duration-200
    ${completed
      ? 'bg-[var(--brand-success)] border-[var(--brand-success)]'
      : 'bg-[var(--bg-primary)] border-[var(--border-default)]'
    }
  `;

  const stepIconStyles = (completed) => `
    ${completed ? 'text-white' : 'text-[var(--text-muted)]'}
  `;

  const stepLabelStyles = (completed) => `
    mt-2
    text-xs font-medium
    text-center
    ${completed ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}
  `;

  const stepLineStyles = (completed) => `
    flex-1
    h-0.5
    mx-2
    ${completed ? 'bg-[var(--brand-success)]' : 'bg-[var(--border-default)]'}
  `;

  const combinedClassName = `${containerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  return (
    <div className={combinedClassName} {...props}>
      {steps.map((step, index) => (
        <React.Fragment key={index}>
          <div className={stepContainerStyles}>
            <div className={stepDotStyles(step.completed)}>
              {step.completed ? (
                <svg
                  className={stepIconStyles(step.completed)}
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M13.3332 4L5.99984 11.3333L2.6665 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              ) : (
                <div className={`w-3 h-3 rounded-full ${stepIconStyles(step.completed)}`} />
              )}
            </div>
            <p className={stepLabelStyles(step.completed)}>
              {step.label}
            </p>
          </div>
          {index < steps.length - 1 && (
            <div className={stepLineStyles(step.completed)} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

export default CvetyStatus;