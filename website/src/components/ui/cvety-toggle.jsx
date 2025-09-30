import React from 'react';

/**
 * CvetyToggle Component
 *
 * Toggle switch component for boolean settings and options in the Cvety.kz design system.
 *
 * @example
 * <CvetyToggle
 *   checked={deliveryEnabled}
 *   onCheckedChange={setDeliveryEnabled}
 *   label="Заказать Яндекс доставку"
 * />
 */

export const CvetyToggle = ({
  checked = false,
  onCheckedChange,
  label,
  disabled = false,
  className = '',
  ...props
}) => {
  const toggleId = React.useId();

  const containerStyles = `
    flex items-center
    ${label ? 'justify-between' : 'justify-start'}
    gap-3
  `;

  const labelStyles = `
    text-base font-normal
    text-[var(--text-primary)]
    flex-1
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
  `;

  const switchContainerStyles = `
    relative inline-flex
    h-6 w-11
    flex-shrink-0
    cursor-pointer
    rounded-full
    border-2 border-transparent
    transition-colors duration-200
    focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:ring-offset-2
    ${checked ? 'bg-[var(--brand-primary)]' : 'bg-[var(--bg-tertiary)]'}
    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
  `;

  const switchThumbStyles = `
    pointer-events-none
    inline-block
    h-5 w-5
    transform rounded-full
    bg-white
    shadow-lg
    ring-0
    transition-transform duration-200
    ${checked ? 'translate-x-5' : 'translate-x-0'}
  `;

  const combinedClassName = `${containerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  const handleToggle = () => {
    if (!disabled && onCheckedChange) {
      onCheckedChange(!checked);
    }
  };

  return (
    <div className={combinedClassName} {...props}>
      {label && (
        <label
          htmlFor={toggleId}
          className={labelStyles}
        >
          {label}
        </label>
      )}
      <button
        id={toggleId}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={handleToggle}
        disabled={disabled}
        className={switchContainerStyles}
      >
        <span className={switchThumbStyles} />
      </button>
    </div>
  );
};

export default CvetyToggle;