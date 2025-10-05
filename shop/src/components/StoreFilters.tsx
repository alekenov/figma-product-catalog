import { useState } from 'react';
import { FilterChips, storePageFilters, storeSections } from './FilterChips';

export function StoreFilters() {
  const [selectedFilters, setSelectedFilters] = useState<string[]>(['all']);
  const [selectedSections, setSelectedSections] = useState<string[]>([]);

  return (
    <div className="space-y-[var(--spacing-3)]">
      {/* Фильтры товаров */}
      <div className="px-[var(--spacing-4)]">
        <FilterChips
          chips={storePageFilters}
          selectedChips={selectedFilters}
          onSelectionChange={setSelectedFilters}
          allowMultiple={false}
        />
      </div>
      
      {/* Секции */}
      <div className="px-[var(--spacing-4)]">
        <FilterChips
          chips={storeSections}
          selectedChips={selectedSections}
          onSelectionChange={setSelectedSections}
          allowMultiple={true}
        />
      </div>
    </div>
  );
}