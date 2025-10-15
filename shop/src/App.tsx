import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ShopProvider } from './contexts/ShopContext';
import { CartProvider } from './contexts/CartContext';
import { OrderFormProvider } from './contexts/OrderFormContext';
import { ShopHomePage } from './components/ShopHomePage';
import { ProductPageCard } from './components/ProductPageCard';
import { CartPage } from './components/CartPage';
import { OrderStatusPage } from './components/OrderStatusPage';

export default function App() {
  return (
    <BrowserRouter>
      <ShopProvider>
        <CartProvider>
          <OrderFormProvider>
            <div className="bg-[var(--background-secondary)] min-h-screen w-full max-w-sm mx-auto">
              <Routes>
                <Route path="/:shopSlug" element={<ShopHomePage />} />
                <Route path="/:shopSlug/product/:productId" element={<ProductPageCard />} />
                <Route path="/:shopSlug/cart" element={<CartPage />} />
                <Route path="/:shopSlug/order/:trackingId" element={<OrderStatusPage />} />
                <Route path="/" element={<Navigate to="/vetka" replace />} />
              </Routes>
            </div>
          </OrderFormProvider>
        </CartProvider>
      </ShopProvider>
    </BrowserRouter>
  );
}
