import { CvetyBadge } from './ui/cvety-badge';
import svgPaths from '../imports/svg-d37n8swoc1';

export function StoreInfo() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
      <h1 className="text-headline text-[var(--text-primary)]">Vetka - магазин цветов</h1>
      
      <div className="flex items-center gap-[var(--spacing-3)] flex-wrap">
        <div className="flex items-center gap-1">
          <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
            <path d={svgPaths.p2eaf7900} fill="var(--brand-primary)" />
          </svg>
          <span className="text-body-emphasis text-[var(--text-primary)]">4.6</span>
        </div>
        <span className="text-caption text-[var(--text-primary)]">164 отзыва</span>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-[var(--brand-success)] rounded-full"></div>
          <span className="text-caption text-[var(--brand-success)]">Открыт</span>
        </div>
        <span className="text-caption text-[var(--text-secondary)]">•</span>
        <span className="text-caption text-[var(--text-secondary)]">до 22:00</span>
      </div>
      

      
      <div className="space-y-[var(--spacing-2)]">
        <div className="text-caption text-[var(--text-secondary)]">Доставка 25 мин • 1 500 ₸</div>
        <div className="flex items-center gap-[var(--spacing-2)]">
          <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
            <path d="M8 2C9.1 2 10 2.9 10 4C10 5.1 9.1 6 8 6C6.9 6 6 5.1 6 4C6 2.9 6.9 2 8 2ZM8 13C10.5 10.5 12 8.5 12 6.5C12 4.5 10.5 2 8 2C5.5 2 4 4.5 4 6.5C4 8.5 5.5 10.5 8 13Z" fill="var(--text-secondary)" />
          </svg>
          <span className="text-caption text-[var(--text-secondary)]">г. Астана, ул. Абая, 15</span>
        </div>
      </div>
    </div>
  );
}