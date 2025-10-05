import { CartMobileHeader } from './CartMobileHeader';
import { CartMobileItems } from './CartMobileItems';
import { CartMobileAddons } from './CartMobileAddons';
import { CartMobileSummary } from './CartMobileSummary';

export function CartMobileRefactored() {
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        {/* Header */}
        <CartMobileHeader />
        
        {/* Content */}
        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)] pt-24">
          {/* Items in Cart */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <CartMobileItems />
          </div>
          
          {/* Add-ons */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <CartMobileAddons />
          </div>
          
          {/* Order Summary */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <CartMobileSummary />
          </div>
        </div>
      </div>
    </div>
  );
}