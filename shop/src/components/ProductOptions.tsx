import { useState } from 'react';

interface SizeOption {
  id: string;
  size: string;
  price: string;
}

function SizeSelector() {
  const [selectedSize, setSelectedSize] = useState('medium');
  
  const sizes: SizeOption[] = [
    { id: 'medium', size: 'M', price: '6 900 ₸' },
    { id: 'large', size: 'L', price: '12 900 ₸' },
    { id: 'xlarge', size: 'XL', price: '15 900 ₸' }
  ];

  return (
    <div className="space-y-[var(--spacing-3)]">
      <h3 className="font-medium text-[var(--text-primary)]">Выберите размер</h3>
      
      <div className={`grid gap-[var(--spacing-2)] ${
        sizes.length === 2 ? 'grid-cols-2' : 
        sizes.length === 4 ? 'grid-cols-2' : 
        'grid-cols-3'
      }`}>
        {sizes.map((size) => (
          <button
            key={size.id}
            onClick={() => setSelectedSize(size.id)}
            className={`relative p-[var(--spacing-3)] rounded-[var(--radius-md)] border transition-all text-center ${
              selectedSize === size.id
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)]'
            }`}
          >
            <div className="space-y-1">
              <div className="font-medium">{size.size}</div>
              <div className="text-sm">{size.price}</div>
            </div>
            
            {selectedSize === size.id && (
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <path 
                    d="M2 5L4 7L8 3" 
                    stroke="white" 
                    strokeWidth="1.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

function AdditionalOptions() {
  return null;
}

export function ProductOptions() {
  return (
    <div className="space-y-[var(--spacing-6)]">
      <SizeSelector />
      <AdditionalOptions />
    </div>
  );
}