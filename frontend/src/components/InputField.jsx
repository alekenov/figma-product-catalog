import React from 'react';

const InputField = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  label,
  helpText,
  error,
  required = false,
  disabled = false,
  maxLength,
  inputMode,
  suffix,
  className = '',
  ...props
}) => {
  const baseInputClasses = `
    w-full text-base font-['Open_Sans'] outline-none transition-colors
    ${disabled ? 'bg-gray-neutral text-gray-disabled cursor-not-allowed' : 'bg-transparent'}
    ${error ? 'text-error-primary' : 'text-black'}
    placeholder-gray-disabled
  `;

  const containerClasses = `
    px-4 py-3 border-b border-gray-border
    ${error ? 'border-error-primary' : 'border-gray-border'}
    ${className}
  `;

  return (
    <div className={containerClasses}>
      {label && (
        <label className="block text-sm text-gray-disabled font-['Open_Sans'] mb-2">
          {label}
          {required && <span className="text-error-primary ml-1">*</span>}
        </label>
      )}

      <div className="flex items-center">
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          maxLength={maxLength}
          inputMode={inputMode}
          className={baseInputClasses}
          {...props}
        />
        {suffix && (
          <span className="text-base font-['Open_Sans'] ml-2 text-gray-disabled">
            {suffix}
          </span>
        )}
      </div>

      {helpText && !error && (
        <p className="text-xs text-gray-disabled mt-1 font-['Open_Sans']">
          {helpText}
        </p>
      )}

      {error && (
        <p className="text-xs text-error-primary mt-1 font-['Open_Sans']">
          {error}
        </p>
      )}
    </div>
  );
};

export default InputField;