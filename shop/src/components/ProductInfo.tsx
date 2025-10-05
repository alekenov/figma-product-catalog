import { Heart, Share2 } from 'lucide-react';

function ProductTitle() {
  return (
    <div className="space-y-[var(--spacing-2)]">
      <h1 className="text-xl font-semibold text-[var(--text-primary)]">
        Букет розовых пионов
      </h1>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-[var(--spacing-3)]">
          <div className="flex items-center gap-1">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="var(--brand-warning)">
              <path d="M7 1L8.5 5H12.5L9.5 7.5L11 12L7 9L3 12L4.5 7.5L1.5 5H5.5L7 1Z" />
            </svg>
            <span className="text-sm text-[var(--text-secondary)]">4.6</span>
          </div>
          <span className="text-sm text-[var(--text-secondary)]">164 отзыва</span>
        </div>
        

      </div>
    </div>
  );
}

function ProductComposition() {
  return (
    <div className="space-y-[var(--spacing-3)]">
      <h3 className="font-medium text-[var(--text-primary)]">Состав</h3>
      <div className="flex items-center justify-between">
        <span className="text-[var(--text-primary)]">Розовые пионы</span>
        <span className="text-[var(--text-secondary)]">5 шт.</span>
      </div>
    </div>
  );
}

export function ProductInfo() {
  return (
    <div className="space-y-[var(--spacing-4)]">
      <ProductTitle />
      <ProductComposition />
    </div>
  );
}