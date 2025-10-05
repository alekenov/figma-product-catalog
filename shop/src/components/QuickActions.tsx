export function QuickActions() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <h2 className="text-title text-[var(--text-primary)]">
        Быстрые действия
      </h2>

      <div className="space-y-[var(--spacing-2)]">
        <button className="w-full flex items-center justify-between p-[var(--spacing-3)] bg-[var(--background-secondary)] rounded-[var(--radius-md)] hover:bg-[var(--neutral-200)] transition-colors">
          <div className="flex items-center gap-[var(--spacing-3)]">
            <div className="w-8 h-8 bg-[var(--neutral-300)] rounded-full flex items-center justify-center">
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
              >
                <circle
                  cx="8"
                  cy="8"
                  r="7"
                  stroke="white"
                  strokeWidth="2"
                />
                <path
                  d="M8 4V8L10 10"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </div>
            <div className="text-left">
              <p className="text-body-emphasis text-[var(--text-primary)]">
                Поддержка
              </p>
              <p className="text-caption text-[var(--text-secondary)]">
                Помощь и FAQ
              </p>
            </div>
          </div>
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
          >
            <path
              d="M6 4L10 8L6 12"
              stroke="var(--text-secondary)"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <button className="w-full flex items-center justify-between p-[var(--spacing-3)] bg-[var(--background-secondary)] rounded-[var(--radius-md)] hover:bg-[var(--neutral-200)] transition-colors">
          <div className="flex items-center gap-[var(--spacing-3)]">
            <div className="w-8 h-8 bg-[var(--neutral-300)] rounded-full flex items-center justify-center">
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
              >
                <path
                  d="M2 3L14 3M2 7L14 7M2 11L14 11"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </div>
            <div className="text-left">
              <p className="text-body-emphasis text-[var(--text-primary)]">
                Условия использования
              </p>
              <p className="text-caption text-[var(--text-secondary)]">
                Правила и политика
              </p>
            </div>
          </div>
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
          >
            <path
              d="M6 4L10 8L6 12"
              stroke="var(--text-secondary)"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}