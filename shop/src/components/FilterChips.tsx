import { useState } from 'react';
import svgPaths from '../imports/svg-548geyzbrr';

export interface FilterChip {
  id: string;
  label: string;
  icon?: 'lightning' | 'star';
}

export interface FilterChipsProps {
  chips: FilterChip[];
  selectedChips?: string[];
  onSelectionChange?: (selectedIds: string[]) => void;
  allowMultiple?: boolean;
  className?: string;
}

export function FilterChips({ 
  chips, 
  selectedChips = [], 
  onSelectionChange,
  allowMultiple = true,
  className = ""
}: FilterChipsProps) {
  const [internalSelected, setInternalSelected] = useState<string[]>(selectedChips);
  
  const selected = onSelectionChange ? selectedChips : internalSelected;
  
  const handleChipClick = (chipId: string) => {
    let newSelected: string[];
    
    if (allowMultiple) {
      newSelected = selected.includes(chipId)
        ? selected.filter(id => id !== chipId)
        : [...selected, chipId];
    } else {
      newSelected = selected.includes(chipId) ? [] : [chipId];
    }
    
    if (onSelectionChange) {
      onSelectionChange(newSelected);
    } else {
      setInternalSelected(newSelected);
    }
  };

  const renderIcon = (iconType: 'lightning' | 'star') => {
    switch (iconType) {
      case 'lightning':
        return (
          <div className="h-[14px] relative shrink-0 w-[8px]">
            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 14">
              <path d={svgPaths.p19d9e300} fill="currentColor" />
            </svg>
          </div>
        );
      case 'star':
        return (
          <div className="relative shrink-0 size-[14px]">
            <div className="absolute bottom-[9.55%] left-[2.45%] right-[2.45%] top-0">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 14 13">
                <path d={svgPaths.p16acdc00} fill="currentColor" />
              </svg>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`flex flex-wrap gap-[var(--spacing-2)] ${className}`}>
      {chips.map((chip) => {
        const isSelected = selected.includes(chip.id);
        
        return (
          <button
            key={chip.id}
            onClick={() => handleChipClick(chip.id)}
            className={`relative flex items-center gap-[3px] h-[32px] px-[10px] py-[5px] rounded-[27px] border transition-all text-label shrink-0 whitespace-nowrap ${
              isSelected
                ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
            }`}
          >
            {chip.icon && renderIcon(chip.icon)}
            <span>{chip.label}</span>
            
            {isSelected && (
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
        );
      })}
    </div>
  );
}

// Готовые наборы фильтров для разных страниц
export const homePageFilters: FilterChip[] = [
  { id: 'urgent', label: 'Срочно', icon: 'lightning' },
  { id: 'budget', label: 'Бюджетные', icon: 'star' },
  { id: 'discounts', label: 'Скидки' },
  { id: 'mono', label: 'Монобукеты' },
  { id: 'roses', label: 'Розы' },
  { id: 'mom', label: 'Маме' },
  { id: 'valentine', label: '14 февраля' },
  { id: 'wholesale', label: 'Оптом' },
  { id: 'pickup', label: 'Самовывоз' }
];

export const storePageFilters: FilterChip[] = [
  { id: 'all', label: 'Все товары' },
  { id: 'fresh', label: 'Свежие' },
  { id: 'premium', label: 'Премиум' }
];

export const storeSections: FilterChip[] = [
  { id: 'sales', label: 'Акции' },
  { id: 'popular', label: 'Популярное' }
];