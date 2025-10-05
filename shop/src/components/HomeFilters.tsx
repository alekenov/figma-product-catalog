import { useState } from 'react';
import { FilterChips, homePageFilters } from './FilterChips';

export function HomeFilters() {
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);

  // Группируем фильтры по рядам как в дизайне
  const filterRows = [
    homePageFilters.slice(0, 3), // Срочно, Бюджетные, Скидки
    homePageFilters.slice(3, 6), // Монобукеты, Розы, Маме
    homePageFilters.slice(6, 9)  // 14 февраля, Оптом, Самовывоз
  ];

  return (
    <div className="space-y-[var(--spacing-2)]">
      {filterRows.map((row, rowIndex) => (
        <FilterChips
          key={rowIndex}
          chips={row}
          selectedChips={selectedFilters}
          onSelectionChange={setSelectedFilters}
          allowMultiple={true}
        />
      ))}
    </div>
  );
}