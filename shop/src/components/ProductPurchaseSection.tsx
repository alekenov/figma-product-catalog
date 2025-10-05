import { Heart, Share2, Shield, ChevronDown } from 'lucide-react';
import { CvetyButton } from './ui/cvety-button';
import { useState } from 'react';

function PriceDisplay() {
  return (
    <div className="flex items-center">
      <span className="text-2xl font-semibold text-[var(--text-primary)]">
        6 900 ₸
      </span>
    </div>
  );
}

function AdditionalOptions() {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  
  const options = [
    { 
      id: 'card', 
      label: 'Открытка', 
      price: '+ 300 ₸',
      image: 'https://images.unsplash.com/photo-1736680839033-b659ef1a44ac?w=200&h=200&fit=crop'
    },
    { 
      id: 'chocolates', 
      label: 'Конфеты', 
      price: '+ 1 500 ₸',
      image: 'https://images.unsplash.com/photo-1607940471713-a9376f150a0d?w=200&h=200&fit=crop'
    },
    { 
      id: 'balloons', 
      label: 'Шары', 
      price: '+ 800 ₸',
      image: 'https://images.unsplash.com/photo-1663310240093-0894c0e6c3d4?w=200&h=200&fit=crop'
    },
    { 
      id: 'package', 
      label: 'Упаковка', 
      price: '+ 500 ₸',
      image: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&h=200&fit=crop'
    }
  ];

  const toggleOption = (optionId: string) => {
    setSelectedOptions(prev => 
      prev.includes(optionId) 
        ? prev.filter(id => id !== optionId)
        : [...prev, optionId]
    );
  };

  return (
    <div className="space-y-[var(--spacing-3)]">
      <h3 className="font-medium text-[var(--text-primary)]">Дополнительно</h3>
      
      <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
        {options.map((option) => (
          <button
            key={option.id}
            onClick={() => toggleOption(option.id)}
            className={`relative p-[var(--spacing-3)] rounded-[var(--radius-md)] border transition-all text-left ${
              selectedOptions.includes(option.id)
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)]'
            }`}
          >
            <div className="space-y-[var(--spacing-2)]">
              <div className="aspect-square rounded-[var(--radius-sm)] overflow-hidden bg-[var(--background-secondary)]">
                <img 
                  src={option.image} 
                  alt={option.label}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="space-y-1">
                <div className="font-medium text-sm">{option.label}</div>
                <div className="text-xs text-[var(--text-secondary)]">{option.price}</div>
              </div>
            </div>
            
            {selectedOptions.includes(option.id) && (
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

function AddToCartButton() {
  return (
    <CvetyButton 
      variant="primary" 
      fullWidth
      className="h-12"
    >
      Добавить в корзину
    </CvetyButton>
  );
}

function GuaranteeSection() {
  return null;
}

export function ProductPurchaseSection() {
  return (
    <div className="space-y-[var(--spacing-4)]">
      {/* Main purchase section */}
      <div className="p-[var(--spacing-6)] bg-white rounded-[var(--radius-md)]">
        <div className="space-y-[var(--spacing-6)]">
          <PriceDisplay />
          
          <div className="space-y-[var(--spacing-4)]">
            <AddToCartButton />
            <AdditionalOptions />
          </div>
        </div>
      </div>
      
      {/* Guarantee section */}
      <GuaranteeSection />
    </div>
  );
}