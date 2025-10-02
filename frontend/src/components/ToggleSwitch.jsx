import React from 'react';

const ToggleSwitch = ({
  isEnabled,
  onToggle,
  size = 'md',
  disabled = false
}) => {
  const sizeClasses = {
    sm: 'h-5 w-9',
    md: 'h-6 w-11',
    lg: 'h-7 w-13'
  };

  const knobSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  const translateClasses = {
    sm: isEnabled ? 'translate-x-4' : 'translate-x-0.5',
    md: isEnabled ? 'translate-x-6' : 'translate-x-1',
    lg: isEnabled ? 'translate-x-7' : 'translate-x-1'
  };

  return (
    <button
      onClick={() => onToggle(!isEnabled)}
      disabled={disabled}
      className={`
        relative inline-flex items-center rounded-full transition-colors
        ${sizeClasses[size]}
        ${isEnabled ? 'bg-green-success' : 'bg-gray-neutral'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      role="switch"
      aria-checked={isEnabled}
    >
      <span
        className={`
          inline-block transform rounded-full bg-white transition-transform
          ${knobSizeClasses[size]}
          ${translateClasses[size]}
        `}
      />
    </button>
  );
};

export default ToggleSwitch;