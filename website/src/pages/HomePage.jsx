import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useHomeProducts, useFilters } from '../hooks/useProductsQuery';
import { formatPrice } from '../utils/price';
import Header from '../components/layout/Header';
import CategoryNav from '../components/layout/CategoryNav';
import Footer from '../components/layout/Footer';
import ProductCard from '../components/ProductCard';
import ProductCardSkeleton from '../components/ProductCardSkeleton';
import SectionHeader from '../components/SectionHeader';
import FilterTags, { FilterIcons } from '../components/FilterTags';
import ReviewsSection from '../components/ReviewsSection';
import FAQSection from '../components/FAQSection';
import CvetyButton from '../components/ui/CvetyButton';

// Tag metadata mapping
const TAG_METADATA = {
  urgent: { label: 'Срочно', icon: <FilterIcons.Lightning /> },
  budget: { label: 'Бюджетные', icon: <FilterIcons.Star /> },
  discount: { label: 'Скидки' },
  roses: { label: 'Розы' },
  mom: { label: 'Маме' },
  valentine: { label: '14 февраля' },
  wholesale: { label: 'Оптом' }
};

export default function HomePage() {
  const navigate = useNavigate();
  const { getCartCount } = useCart();
  const [activeTags, setActiveTags] = useState([]);

  // Fetch data from API using React Query
  const {
    data: homeData,
    isLoading: productsLoading,
    error: productsError
  } = useHomeProducts(null, activeTags);

  const {
    data: filters = {},
    isLoading: filtersLoading
  } = useFilters();

  // Extract products from homeData
  const products = homeData?.products || [];

  // Transform API tags to UI format
  const uiTags = useMemo(() => {
    return (filters.tags || []).map(tagId => ({
      id: tagId,
      label: TAG_METADATA[tagId]?.label || tagId,
      icon: TAG_METADATA[tagId]?.icon
    }));
  }, [filters.tags]);

  // Transform API products to UI format
  const uiProducts = useMemo(() => {
    return products.map(product => ({
      id: product.id,
      image: product.image,
      price: formatPrice(product.price),
      name: product.name,
      deliveryText: 'Доставим завтра' // TODO: Calculate from manufacturingTime
    }));
  }, [products]);

  const handleTagClick = (tagId) => {
    setActiveTags(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleClearFilters = () => {
    setActiveTags([]);
  };

  const handleAddToCart = (productId) => {
    console.log('Add to cart:', productId);
  };

  const handleProductClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  // Check if we have filtered results
  const hasActiveFilters = activeTags.length > 0;
  const showEmptyState = !productsLoading && !productsError && hasActiveFilters && uiProducts.length === 0;

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      {/* Header */}
      <Header cartCount={getCartCount()} />

      {/* Category Navigation */}
      <CategoryNav />

      {/* Main Content */}
      <main className="flex-1 px-4 py-6 space-y-6">
          {/* Page Title + Filter Button */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h1 className="font-sans font-bold leading-normal text-h2 text-text-black">
                Доставка цветов в Астане
              </h1>
              {/* Clear filters button */}
              {hasActiveFilters && (
                <CvetyButton
                  variant="link"
                  size="sm"
                  onClick={handleClearFilters}
                  className="text-text-grey-dark hover:text-pink"
                  leftIcon={
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M12 4L4 12M4 4l8 8"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  }
                >
                  Сбросить
                </CvetyButton>
              )}
            </div>
            <div className="relative">
              <CvetyButton
                variant="ghost"
                size="sm"
                aria-label="Фильтры"
                rightIcon={
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M4 6h16M7 12h10M10 18h4"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                }
              >
                Фильтры
              </CvetyButton>
              {/* Active filters badge */}
              {hasActiveFilters && (
                <div className="absolute -top-1 -right-1 bg-pink text-white text-body-2 font-bold w-5 h-5 rounded-full flex items-center justify-center">
                  {activeTags.length}
                </div>
              )}
            </div>
          </div>

          {/* Filter Tags */}
          {filtersLoading ? (
            <div className="text-center py-4 text-text-grey-dark">Загрузка фильтров...</div>
          ) : (
            <FilterTags
              tags={uiTags}
              activeTags={activeTags}
              onTagClick={handleTagClick}
            />
          )}

          {/* Bestsellers Section */}
          <div className="space-y-4">
            <SectionHeader
              title="Букеты-бестселлеры"
              onShowAll={() => console.log('Show all bestsellers')}
            />

            {/* Loading State - Skeleton Screens */}
            {productsLoading && (
              <div className="grid grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                  <ProductCardSkeleton key={i} />
                ))}
              </div>
            )}

            {/* Error State */}
            {productsError && (
              <div className="text-center py-8 text-brand-error">
                <p>Ошибка загрузки: {productsError?.message || 'Неизвестная ошибка'}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-2 text-pink underline"
                >
                  Попробовать снова
                </button>
              </div>
            )}

            {/* Empty State - No results after filtering */}
            {showEmptyState && (
              <div className="col-span-2 flex flex-col items-center justify-center py-12 px-4">
                {/* Search icon */}
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="mb-4 text-text-muted">
                  <circle cx="20" cy="20" r="8" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <path d="M26 26L32 32" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>

                <h3 className="text-h3 text-text-black mb-2">Ничего не найдено</h3>
                <p className="text-body-2 text-text-grey-dark mb-4 text-center">
                  Попробуйте изменить выбранные фильтры
                </p>

                <CvetyButton
                  variant="secondary"
                  size="md"
                  onClick={handleClearFilters}
                >
                  Сбросить фильтры
                </CvetyButton>
              </div>
            )}

            {/* Product Grid - 2 columns with fade animation */}
            {!productsLoading && !productsError && !showEmptyState && (
              <div className="grid grid-cols-2 gap-4 transition-opacity duration-300 opacity-100">
                {uiProducts.map(product => (
                  <div key={product.id} className="animate-fadeIn">
                    <ProductCard
                      image={product.image}
                      price={product.price}
                      name={product.name}
                      deliveryText={product.deliveryText}
                      onAddToCart={() => handleAddToCart(product.id)}
                      onClick={() => handleProductClick(product.id)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Reviews Section */}
          <ReviewsSection onShowAll={() => console.log('Show all reviews')} />

          {/* FAQ Section */}
          <FAQSection />
        </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}