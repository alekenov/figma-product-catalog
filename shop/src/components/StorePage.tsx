import { Header } from './Header';
import { Footer } from './Footer';
import { StoreInfo } from './StoreInfo';
import { StoreFilters } from './StoreFilters';
import { StoreProducts } from './StoreProducts';
import { StoreReviews } from './StoreReviews';

interface StorePageProps {
  storeId?: string;
}

export function StorePage({ storeId = "vetka" }: StorePageProps) {
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header />
        
        <div className="space-y-[var(--spacing-4)] pb-[var(--spacing-8)]">
          <div className="p-[var(--spacing-4)]">
            <StoreInfo />
          </div>
          <StoreFilters />
          <div className="p-[var(--spacing-4)]">
            <StoreProducts />
          </div>
          <div className="p-[var(--spacing-4)]">
            <StoreReviews />
          </div>
        </div>
        
        <Footer />
      </div>
    </div>
  );
}