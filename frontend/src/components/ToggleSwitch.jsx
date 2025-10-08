import React from 'react';

const ToggleSwitch = ({
  isEnabled,
  checked,
  onToggle,
  onChange,
  size = 'md',
  disabled = false
}) => {
  // Support both prop names for compatibility
  const enabled = checked !== undefined ? checked : isEnabled;
  const handleToggle = onChange || onToggle;

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
    sm: enabled ? 'translate-x-4' : 'translate-x-0.5',
    md: enabled ? 'translate-x-6' : 'translate-x-1',
    lg: enabled ? 'translate-x-7' : 'translate-x-1'
  };

  const handleClick = () => {
    if (handleToggle) {
      handleToggle(!enabled);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`
        relative inline-flex items-center rounded-full transition-colors
        ${sizeClasses[size]}
        ${enabled ? 'bg-green-success' : 'bg-gray-neutral'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      role="switch"
      aria-checked={enabled}
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