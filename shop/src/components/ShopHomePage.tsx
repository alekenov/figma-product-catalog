/**
 * Shop Home Page
 * Displays products for the current shop
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useCart } from '../contexts/CartContext';
import { fetchShopProducts, Product } from '../services/shopApi';
import { CvetyCard, CvetyCardContent } from './ui/cvety-card';
import { CvetyButton } from './ui/cvety-button';
import { Header } from './Header';

export function ShopHomePage() {
  const navigate = useNavigate();
  const { shopSlug } = useParams();
  const { shopConfig, shopInfo, isShopOpen } = useShop();
  const { itemCount } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadProducts() {
      if (!shopConfig) return;

      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchShopProducts(shopConfig.id, { limit: 50, enabledOnly: true });
        setProducts(data);
      } catch (err) {
        console.error('[ShopHomePage] Failed to load products:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }

    loadProducts();
  }, [shopConfig]);

  if (!shopConfig || !shopInfo) {
    return null; // ShopContext handles loading state
  }

  const handleNavigate = (page: string, data?: any) => {
    if (page === 'product' && data?.productId) {
      navigate(`/${shopSlug}/product/${data.productId}`);
    } else if (page === 'cart') {
      navigate(`/${shopSlug}/cart`);
    } else if (page === 'home') {
      navigate(`/${shopSlug}`);
    } else if (page === 'order-status' && data?.trackingId) {
      navigate(`/${shopSlug}/order/${data.trackingId}`);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background-secondary)] pb-20">
      {/* Shop Header */}
      <div className="bg-white border-b border-[var(--border)]">
        <div className="px-[var(--spacing-4)]">
          <Header onNavigate={handleNavigate} itemCount={itemCount} />
        </div>

        {/* Shop Info */}
        <div className="px-[var(--spacing-4)] pb-[var(--spacing-3)]">
          <div className="flex items-center gap-2 text-sm mb-3">
            <span className={`inline-flex items-center gap-1 ${isShopOpen ? 'text-green-600' : 'text-red-600'}`}>
              <span className={`w-2 h-2 rounded-full ${isShopOpen ? 'bg-green-600' : 'bg-red-600'}`}></span>
              {isShopOpen ? 'Открыто' : 'Закрыто'}
            </span>
            {shopInfo.city && <span className="text-[var(--text-secondary)]">• {shopInfo.city}</span>}
          </div>

          {/* Shop Info Cards */}
          <div className="grid grid-cols-2 gap-2">
            {shopInfo.delivery_available && (
              <div className="bg-[var(--background-secondary)] rounded-xl p-2">
                <div className="text-xs text-[var(--text-secondary)]">Доставка</div>
                <div className="text-sm font-semibold text-[var(--text-primary)]">
                  {shopInfo.delivery_cost_tenge} ₸
                </div>
              </div>
            )}
            {shopInfo.pickup_available && (
              <div className="bg-[var(--background-secondary)] rounded-xl p-2">
                <div className="text-xs text-[var(--text-secondary)]">Самовывоз</div>
                <div className="text-sm font-semibold text-[var(--text-primary)]">Бесплатно</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Products Section */}
      <div className="p-[var(--spacing-4)]">
        <h2 className="text-[var(--heading-2)] font-bold text-[var(--text-primary)] mb-4">
          Наши букеты
        </h2>

        {/* Loading State */}
        {isLoading && (
          <div className="grid grid-cols-2 gap-3">
            {[...Array(6)].map((_, i) => (
              <CvetyCard key={i} className="animate-pulse">
                <div className="aspect-square bg-gray-200 rounded-t-2xl"></div>
                <CvetyCardContent className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CvetyCardContent>
              </CvetyCard>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="text-center py-8">
            <p className="text-red-500 mb-4">Ошибка загрузки товаров</p>
            <CvetyButton onClick={() => window.location.reload()}>
              Попробовать снова
            </CvetyButton>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && products.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌸</div>
            <p className="text-[var(--text-secondary)]">
              Пока нет товаров в магазине
            </p>
          </div>
        )}

        {/* Products Grid */}
        {!isLoading && !error && products.length > 0 && (
          <div className="grid grid-cols-2 gap-3">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} shopSlug={shopSlug || 'vetka'} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Product Card Component
 */
interface ProductCardProps {
  product: Product;
  shopSlug: string;
}

function ProductCard({ product, shopSlug }: ProductCardProps) {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [isAdding, setIsAdding] = useState(false);

  // Get primary image or fallback
  const primaryImage = product.images.find(img => img.is_primary)?.url || product.images[0]?.url || product.image;

  // Format price in tenge (prices are stored in kopecks)
  const priceInTenge = Math.floor(product.price / 100);

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click when clicking add button
    setIsAdding(true);
    addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      image: primaryImage,
    });

    // Show animation feedback
    setTimeout(() => setIsAdding(false), 500);
  };

  const handleCardClick = () => {
    navigate(`/${shopSlug}/product/${product.id}`);
  };

  return (
    <CvetyCard
      className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
      onClick={handleCardClick}
    >
      {/* Product Image */}
      <div className="aspect-square bg-gray-100 relative overflow-hidden">
        {primaryImage ? (
          <img
            src={primaryImage}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Product Info */}
      <CvetyCardContent className="p-3">
        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1 line-clamp-2">
          {product.name}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-[var(--brand-primary)]">
            {priceInTenge.toLocaleString()} ₸
          </span>
          <CvetyButton
            size="sm"
            variant={isAdding ? "default" : "ghost"}
            className="text-xs"
            onClick={handleAddToCart}
            disabled={isAdding}
          >
            {isAdding ? '✓' : '+'}
          </CvetyButton>
        </div>
      </CvetyCardContent>
    </CvetyCard>
  );
}
