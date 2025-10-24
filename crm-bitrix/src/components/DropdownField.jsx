import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export function DropdownField({
  label,
  value,
  options = [],
  onChange,
  disabled = false,
  showBorder = true
}) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedOption = options.find(opt => opt.value === value);
  const displayValue = selectedOption?.label || value || 'Выбрать';

  return (
    <div className={showBorder ? 'border-t border-gray-border pt-4 mt-4' : ''}>
      <p className="text-sm text-gray-placeholder font-sans mb-2">{label}</p>
      <div className="relative">
        <button
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className="w-full flex items-center justify-between px-3 py-2 border border-gray-border rounded text-left disabled:opacity-50"
        >
          <span className="font-sans text-[16px] text-black">{displayValue}</span>
          <ChevronDown size={10} className="text-gray-placeholder flex-shrink-0" />
        </button>

        {isOpen && !disabled && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-border rounded z-10 shadow-lg">
            {options.length > 0 ? (
              <div className="max-h-48 overflow-y-auto">
                {options.map((option, index) => (
                  <button
                    key={option.value}
                    onClick={() => {
                      onChange?.(option.value);
                      setIsOpen(false);
                    }}
                    className={`w-full px-3 py-2 text-left font-sans text-[16px] hover:bg-violet-light transition ${
                      value === option.value ? 'bg-purple-primary text-white' : 'text-black'
                    } ${index > 0 ? 'border-t border-gray-border' : ''}`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            ) : (
              <div className="px-3 py-2 text-gray-placeholder font-sans text-[14px]">
                Нет опций
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default DropdownField;
