import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between bg-white hover:bg-gray-50 transition"
      >
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        <ChevronDown
          size={20}
          className={`text-gray-600 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isOpen && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 space-y-4">
          {children}
        </div>
      )}
    </div>
  );
}
