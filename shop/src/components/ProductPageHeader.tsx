import { Header } from './Header';
import svgPaths from '../imports/svg-bdl3k6yajx';

export function ProductPageHeader() {
  return (
    <div>
      <Header />
      <div className="px-[var(--spacing-4)]">
        <div className="border-b border-[var(--border)] py-[var(--spacing-2)]">
          <button className="flex items-center gap-1">
            <div className="w-5 h-5">
              <svg viewBox="0 0 19 19" fill="none">
                <path d={svgPaths.p32543000} fill="var(--text-primary)" />
              </svg>
            </div>
            <p className="text-sm text-[var(--text-primary)]">
              <span className="font-semibold">Астана</span>, уточните адрес доставки...
            </p>
          </button>
        </div>
      </div>
    </div>
  );
}