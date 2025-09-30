import React from 'react';

/**
 * CvetyInput Component
 *
 * Input field component for all form inputs in the Cvety.kz design system.
 * Always provide label prop for accessibility.
 * Supports both input and textarea via 'as' prop.
 *
 * @example
 * <CvetyInput
 *   label="Email"
 *   placeholder="Введите email..."
 *   error={true}
 *   helperText="Неверный формат email"
 * />
 *
 * @example
 * <CvetyInput
 *   as="textarea"
 *   label="Комментарий"
 *   rows={3}
 *   placeholder="Ваш комментарий..."
 * />
 */

export const CvetyInput = ({
  as = 'input',
  label,
  type = 'text',
  placeholder = '',
  value,
  onChange,
  onBlur,
  onFocus,
  error = false,
  helperText = '',
  disabled = false,
  required = false,
  rows = 3,
  resize = false,
  className = '',
  inputClassName = '',
  ...props
}) => {
  const inputId = React.useId();

  const containerStyles = `
    w-full
  `;

  const labelStyles = `
    block mb-1.5
    text-sm font-medium
    text-[var(--text-primary)]
    ${required ? "after:content-['*'] after:ml-0.5 after:text-[var(--brand-error)]" : ''}
  `;

  const inputBaseStyles = `
    w-full px-4 py-3
    text-base font-normal
    text-[var(--text-primary)]
    bg-[var(--bg-primary)]
    border rounded-lg
    transition-colors duration-200
    placeholder:text-[var(--text-secondary)]
    focus:outline-none focus:ring-2 focus:ring-offset-0
    disabled:bg-[var(--bg-secondary)] disabled:cursor-not-allowed
    ${as === 'textarea' && !resize ? 'resize-none' : ''}
  `;

  const inputStateStyles = error
    ? `
      border-[var(--brand-error)]
      focus:border-[var(--brand-error)]
      focus:ring-[var(--brand-error)]
    `
    : `
      border-[var(--border-default)]
      focus:border-[var(--brand-primary)]
      focus:ring-[var(--brand-primary)]
    `;

  const helperTextStyles = `
    mt-1.5 text-xs
    ${error ? 'text-[var(--brand-error)]' : 'text-[var(--text-secondary)]'}
  `;

  const combinedInputClassName = `
    ${inputBaseStyles}
    ${inputStateStyles}
    ${inputClassName}
  `.replace(/\s+/g, ' ').trim();

  const combinedContainerClassName = `${containerStyles} ${className}`.replace(/\s+/g, ' ').trim();

  const Component = as === 'textarea' ? 'textarea' : 'input';

  return (
    <div className={combinedContainerClassName}>
      {label && (
        <label htmlFor={inputId} className={labelStyles}>
          {label}
        </label>
      )}
      <Component
        id={inputId}
        type={as === 'input' ? type : undefined}
        rows={as === 'textarea' ? rows : undefined}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        disabled={disabled}
        required={required}
        className={combinedInputClassName}
        aria-invalid={error}
        aria-describedby={helperText ? `${inputId}-helper` : undefined}
        {...props}
      />
      {helperText && (
        <p id={`${inputId}-helper`} className={helperTextStyles}>
          {helperText}
        </p>
      )}
    </div>
  );
};

export default CvetyInput;