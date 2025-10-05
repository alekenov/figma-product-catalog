import { useState } from 'react';

export function MinimalFooter() {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <footer className="bg-white border-t border-[var(--border)] mt-auto">
      <div className="w-full max-w-sm mx-auto">
        {/* Основная информация */}
        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-4)]">
          {/* Помощь */}
          <div className="space-y-[var(--spacing-2)]">
            <button
              onClick={() => toggleSection('help')}
              className="w-full flex items-center justify-between py-2 text-[var(--text-primary)] font-medium"
            >
              <span>Нужна помощь?</span>
              <svg 
                width="16" 
                height="16" 
                viewBox="0 0 16 16" 
                fill="none"
                className={`transition-transform ${expandedSection === 'help' ? 'rotate-180' : ''}`}
              >
                <path 
                  d="M4 6L8 10L12 6" 
                  stroke="currentColor" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            
            {expandedSection === 'help' && (
              <div className="space-y-[var(--spacing-3)] pl-2">
                <a 
                  href="tel:+77172999888"
                  className="flex items-center gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--background-secondary)] hover:bg-[var(--neutral-200)] transition-colors"
                >
                  <div className="w-8 h-8 bg-[var(--brand-primary)] rounded-full flex items-center justify-center flex-shrink-0">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path 
                        d="M14.5 11.5C14.5 11.5 13.5 12.5 13 13C12.5 13.5 11.5 13.5 11 13C9 11 5 7 3 5C2.5 4.5 2.5 3.5 3 3C3.5 2.5 4.5 1.5 4.5 1.5C5 1 5 1 5.5 1.5L7 3C7.5 3.5 7.5 4.5 7 5C7 5 6.5 5.5 6 6C6.5 7 9 9.5 10 10C10.5 9.5 11 9 11 9C11.5 8.5 12.5 8.5 13 9L14.5 10.5C15 11 15 11 14.5 11.5Z" 
                        fill="white"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-[var(--text-primary)]">
                      +7 (717) 299-98-88
                    </p>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Звонок бесплатный
                    </p>
                  </div>
                </a>
                
                <a 
                  href="https://wa.me/77172999888"
                  className="flex items-center gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--background-secondary)] hover:bg-[var(--neutral-200)] transition-colors"
                >
                  <div className="w-8 h-8 bg-[var(--brand-success)] rounded-full flex items-center justify-center flex-shrink-0">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path 
                        d="M8 1C4.13 1 1 4.13 1 8C1 9.29 1.35 10.5 1.97 11.54L1 15L4.46 14.03C5.5 14.65 6.71 15 8 15C11.87 15 15 11.87 15 8C15 4.13 11.87 1 8 1ZM11.5 11C11.36 11.31 10.96 11.59 10.61 11.67C10.33 11.74 9.98 11.8 8.97 11.4C7.71 10.9 6.31 9.5 5.81 8.24C5.56 7.61 5.56 7.11 5.8 6.7C5.94 6.44 6.19 6.31 6.36 6.31H6.81C6.94 6.31 7.09 6.3 7.17 6.56L7.67 7.81C7.74 7.97 7.7 8.17 7.56 8.31L7.31 8.56C7.31 8.56 7.31 8.81 7.81 9.56S8.69 10.19 8.69 10.19L8.94 9.94C9.08 9.8 9.28 9.76 9.44 9.83L10.69 10.33C10.95 10.41 10.94 10.56 10.94 10.69C10.94 10.81 10.81 11.06 10.55 11.2C10.53 11.21 10.51 11.21 10.5 11.21L11.5 11Z" 
                        fill="white"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-[var(--text-primary)]">
                      WhatsApp
                    </p>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Быстрая поддержка
                    </p>
                  </div>
                </a>
              </div>
            )}
          </div>

          {/* Гарантии */}
          <div className="space-y-[var(--spacing-2)]">
            <button
              onClick={() => toggleSection('guarantees')}
              className="w-full flex items-center justify-between py-2 text-[var(--text-primary)] font-medium"
            >
              <span>Наши гарантии</span>
              <svg 
                width="16" 
                height="16" 
                viewBox="0 0 16 16" 
                fill="none"
                className={`transition-transform ${expandedSection === 'guarantees' ? 'rotate-180' : ''}`}
              >
                <path 
                  d="M4 6L8 10L12 6" 
                  stroke="currentColor" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            
            {expandedSection === 'guarantees' && (
              <div className="space-y-[var(--spacing-2)] pl-2">
                <div className="flex items-start gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--background-secondary)]">
                  <div className="w-6 h-6 bg-[var(--brand-success)] rounded-full flex items-center justify-center mt-0.5 flex-shrink-0">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path 
                        d="M2 6L4.5 8.5L10 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">
                      Свежесть цветов
                    </p>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Только самые свежие цветы от проверенных поставщиков
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--background-secondary)]">
                  <div className="w-6 h-6 bg-[var(--brand-success)] rounded-full flex items-center justify-center mt-0.5 flex-shrink-0">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path 
                        d="M2 6L4.5 8.5L10 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">
                      Доставка вовремя
                    </p>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Доставим точно в указанное время или вернем деньги
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--background-secondary)]">
                  <div className="w-6 h-6 bg-[var(--brand-success)] rounded-full flex items-center justify-center mt-0.5 flex-shrink-0">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path 
                        d="M2 6L4.5 8.5L10 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">
                      Фото доставки
                    </p>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Получите фото с места доставки для спокойствия
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Нижняя часть */}
        <div className="px-[var(--spacing-4)] py-[var(--spacing-3)] border-t border-[var(--border)] bg-[var(--background-secondary)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path 
                    d="M7 1L8.5 5.5H13L9.5 8.5L11 13L7 10L3 13L4.5 8.5L1 5.5H5.5L7 1Z" 
                    fill="white"
                  />
                </svg>
              </div>
              <span className="font-medium text-[var(--text-primary)]">Cvety.kz</span>
            </div>
            
            <div className="text-sm text-[var(--text-secondary)]">
              © 2024
            </div>
          </div>
          
          <div className="mt-2 text-xs text-[var(--text-secondary)] text-center">
            Доставка цветов по Астане и Алматы
          </div>
        </div>
      </div>
    </footer>
  );
}