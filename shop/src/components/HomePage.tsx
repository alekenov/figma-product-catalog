import { Header } from './Header';
import { Footer } from './Footer';
import { LocationSelector } from './LocationSelector';
import { CategoryNavigation } from './CategoryNavigation';
import { MainContent } from './MainContent';
import { HomeFilters } from './HomeFilters';

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface HomePageProps {
  onNavigate: (page: PageType, data?: { storeId?: string; productId?: string }) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header onNavigate={onNavigate} />

        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
          <LocationSelector />
          <CategoryNavigation />
          <HomeFilters />
          <MainContent onNavigate={onNavigate} />
        </div>

        <Footer onNavigate={onNavigate} />
      </div>
    </div>
  );
}