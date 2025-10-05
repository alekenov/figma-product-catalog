import svgPaths from "../imports/svg-rauipwsa5m";

function ArrowIcon() {
  return (
    <div className="relative shrink-0 size-[19px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 19 19">
        <path d={svgPaths.p32543000} fill="var(--text-primary)" />
      </svg>
    </div>
  );
}

export function LocationSelector() {
  return (
    <div className="border-b border-[var(--border)] pb-[var(--spacing-4)]">
      <button className="flex items-center gap-1 px-[var(--spacing-3)] py-[var(--spacing-2)] hover:bg-[var(--background-muted)] rounded-full transition-colors">
        <ArrowIcon />
        <span className="text-body text-[var(--text-primary)]">Астана, ул. Достык 3</span>
      </button>
    </div>
  );
}