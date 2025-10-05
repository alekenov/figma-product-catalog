import { CvetyCard } from './ui/cvety-card';

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface FooterProps {
  onNavigate?: (page: PageType, data?: { storeId?: string; productId?: string }) => void;
}

export function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="bg-[var(--background-muted)] px-[var(--spacing-4)] py-[var(--spacing-6)] space-y-[var(--spacing-6)]">
      <div className="grid grid-cols-2 gap-[var(--spacing-6)]">
        <div className="space-y-[var(--spacing-3)]">
          <h4 className="text-subtitle text-[var(--text-primary)]">Покупателям</h4>
          <div className="space-y-1">
            <button onClick={() => onNavigate?.('stores-list')} className="text-caption text-[var(--text-secondary)] hover:text-[var(--text-primary)]">Магазины</button>
            <p className="text-caption text-[var(--text-secondary)]">Доставка</p>
            <p className="text-caption text-[var(--text-secondary)]">Отзывы</p>
            <p className="text-caption text-[var(--text-secondary)]">Гарантии</p>
          </div>
        </div>

        <div className="space-y-[var(--spacing-3)]">
          <h4 className="text-subtitle text-[var(--text-primary)]">Компания</h4>
          <div className="space-y-1">
            <p className="text-caption text-[var(--text-secondary)]">Контакты</p>
            <p className="text-caption text-[var(--text-secondary)]">О нас</p>
            <p className="text-caption text-[var(--text-secondary)]">Вакансии</p>
          </div>
        </div>
      </div>

      <div className="space-y-[var(--spacing-4)]">
        <p className="text-caption text-[var(--text-primary)]">© Сvety.kz, 2025</p>
        
        <div className="flex gap-[var(--spacing-3)]">
          <div className="w-6 h-6 bg-[var(--text-primary)] rounded-full flex items-center justify-center">
            <div className="w-4 h-4">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 2.04C6.5 2.04 2 6.53 2 12.06C2 22 12 22 12 22S22 22 22 12.06C22 6.53 17.5 2.04 12 2.04ZM16.25 8.46C16.25 8.46 14.9 7.46 12.72 7.46C10.54 7.46 9.19 8.46 9.19 8.46C8.86 8.75 8.86 9.25 9.19 9.54C9.52 9.83 10.02 9.83 10.35 9.54C10.35 9.54 11.27 8.83 12.72 8.83C14.17 8.83 15.09 9.54 15.09 9.54C15.42 9.83 15.92 9.83 16.25 9.54C16.58 9.25 16.58 8.75 16.25 8.46Z" fill="white"/>
              </svg>
            </div>
          </div>
          <div className="w-6 h-6 bg-[var(--text-primary)] rounded-full flex items-center justify-center">
            <div className="w-4 h-4">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z" fill="white"/>
              </svg>
            </div>
          </div>
          <div className="w-6 h-6 bg-[var(--text-primary)] rounded-full flex items-center justify-center">
            <div className="w-4 h-4">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" fill="white"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="flex gap-[var(--spacing-2)]">
          <CvetyCard variant="default" className="p-[var(--spacing-2)]">
            <span className="text-[#005CA9]">VISA</span>
          </CvetyCard>
          <CvetyCard variant="default" className="p-[var(--spacing-2)] flex">
            <div className="w-2 h-3 bg-[#FE0000] rounded-l"></div>
            <div className="w-2 h-3 bg-[#FE9A00] rounded-r"></div>
          </CvetyCard>
          <CvetyCard variant="default" className="p-[var(--spacing-2)]">
            <span className="text-orange-500">Kaspi</span>
          </CvetyCard>
        </div>
      </div>

      <div className="space-y-[var(--spacing-3)]">
        <h4 className="text-subtitle text-[var(--text-primary)]">Приложение</h4>
        <div className="flex gap-[var(--spacing-2)]">
          <div className="bg-[var(--text-primary)] rounded px-3 py-2">
            <span className="text-caption text-white">App Store</span>
          </div>
          <div className="bg-[var(--text-primary)] rounded px-3 py-2">
            <span className="text-caption text-white">Google Play</span>
          </div>
        </div>
      </div>
    </footer>
  );
}