import { ProductCardHeader } from './ProductCardHeader';
import { ProductCardGallery } from './ProductCardGallery';
import { ProductCardDetails } from './ProductCardDetails';
import { ProductCardFooter } from './ProductCardFooter';

// Main refactored product card component
export default function ProductCardRefactored() {
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen flex flex-col">
        <ProductCardHeader />
        
        <div className="flex-1">
          <ProductCardGallery />
          <ProductCardDetails />
        </div>
        
        <ProductCardFooter />
      </div>
    </div>
  );
}