// Компактный футер для страницы магазина
export function StorePageFooter() {
  return (
    <footer className="bg-[var(--background-secondary)] border-t border-[var(--border)]">
      <div className="w-full max-w-sm mx-auto p-[var(--spacing-4)]">
        {/* Основная программа лояльности */}
        <div className="mb-[var(--spacing-4)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path 
                  d="M7 1L8.5 5.5H13L9.5 8.5L11 13L7 10L3 13L4.5 8.5L1 5.5H5.5L7 1Z" 
                  fill="white"
                />
              </svg>
            </div>
            <div>
              <p className="text-body-emphasis text-[var(--text-primary)]">Cvety Stars</p>
              <p className="text-caption text-[var(--text-secondary)]">Программа лояльности</p>
            </div>
          </div>
          <p className="text-caption text-[var(--text-secondary)]">
            Получайте баллы за каждый заказ и тратьте их на скидки
          </p>
        </div>

        {/* Быстрые контакты */}
        <div className="mb-[var(--spacing-4)] space-y-3">
          <a 
            href="tel:+77172999888"
            className="flex items-center gap-3 p-[var(--spacing-3)] rounded-[var(--radius-md)] bg-white hover:bg-[var(--background-muted)] transition-colors"
          >
            <div className="w-6 h-6 bg-[var(--brand-primary)] rounded-full flex items-center justify-center flex-shrink-0">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path 
                  d="M10.5 8.5C10.5 8.5 9.5 9.5 9 10C8.5 10.5 7.5 10.5 7 10C5 8 3 6 2 4C1.5 3.5 1.5 2.5 2 2C2.5 1.5 3.5 0.5 3.5 0.5C4 0 4 0 4.5 0.5L6 2C6.5 2.5 6.5 3.5 6 4C6 4 5.5 4.5 5 5C5.5 6 7 7.5 8 8C8.5 7.5 9 7 9 7C9.5 6.5 10.5 6.5 11 7L10.5 8.5C11 9 11 9 10.5 8.5Z" 
                  fill="white"
                />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-label text-[var(--text-primary)]">
                +7 (717) 299-98-88
              </p>
              <p className="text-micro text-[var(--text-secondary)]">
                Поддержка 24/7
              </p>
            </div>
          </a>
          
          <a 
            href="https://wa.me/77172999888"
            className="flex items-center gap-3 p-[var(--spacing-3)] rounded-[var(--radius-md)] bg-white hover:bg-[var(--background-muted)] transition-colors"
          >
            <div className="w-6 h-6 bg-[var(--brand-success)] rounded-full flex items-center justify-center flex-shrink-0">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path 
                  d="M6 0.5C2.69 0.5 0 3.19 0 6.5C0 7.64 0.26 8.72 0.74 9.66L0 12L2.34 11.26C3.28 11.74 4.36 12 5.5 12H6C9.31 12 12 9.31 12 6C12 2.69 9.31 0.5 6 0.5ZM8.75 8.25C8.64 8.51 8.31 8.74 8.01 8.80C7.78 8.86 7.48 8.90 6.73 8.55C5.78 8.10 4.73 7.25 4.35 6.43C4.17 6.01 4.17 5.63 4.35 5.28C4.46 5.08 4.64 4.98 4.77 4.98H5.11C5.21 4.98 5.32 4.97 5.38 5.17L5.75 6.11C5.81 6.23 5.78 6.38 5.67 6.48L5.48 6.67C5.48 6.67 5.48 6.86 5.86 7.42S6.52 7.89 6.52 7.89L6.71 7.70C6.81 7.60 6.96 7.57 7.08 7.62L8.02 7.99C8.22 8.05 8.21 8.17 8.21 8.27C8.21 8.36 8.11 8.54 7.91 8.65C7.90 8.66 7.88 8.66 7.87 8.66L8.75 8.25Z" 
                  fill="white"
                />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-label text-[var(--text-primary)]">
                WhatsApp
              </p>
              <p className="text-micro text-[var(--text-secondary)]">
                Быстрая поддержка
              </p>
            </div>
          </a>
        </div>

        {/* Краткая информация о компании */}
        <div className="text-center text-micro text-[var(--text-secondary)] space-y-1">
          <p>© 2024 Cvety.kz</p>
          <p>Доставка цветов по Астане и Алматы</p>
        </div>
      </div>
    </footer>
  );
}