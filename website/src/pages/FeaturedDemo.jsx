import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useHomeProducts } from '../hooks/useProductsQuery';
import { formatPrice } from '../utils/price';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import FeaturedProductCard from '../components/FeaturedProductCard';
import PopularStores from '../components/PopularStores';
import PlatformReviewsSection from '../components/PlatformReviewsSection';
import SectionHeader from '../components/SectionHeader';
import ProductCardSkeleton from '../components/ProductCardSkeleton';

/**
 * FeaturedDemo - демо-страница для показа новых компонентов
 * - FeaturedProductCard: https://www.figma.com/design/oRRU0Oblqur76wzfnminmd/Untitled?node-id=1-194
 * - PopularStores: https://www.figma.com/design/oRRU0Oblqur76wzfnminmd/Untitled?node-id=1-354
 * - PlatformReviewsSection: https://www.figma.com/design/oRRU0Oblqur76wzfnminmd/Untitled?node-id=1-413
 *
 * Использует реальные данные из API для продуктов, тестовые данные для магазинов и отзывов (пока нет API)
 */
export default function FeaturedDemo() {
  const navigate = useNavigate();
  const { getCartCount, addToCart } = useCart();

  // Тестовые данные для магазинов (пока нет API)
  const testStores = [
    {
      id: 1,
      image: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=800&h=400&fit=crop',
      badgeText: 'Лучший рейтинг',
      badgeColor: 'green',
      name: 'Vetka - магазин цветов',
      rating: 4.6,
      reviewsCount: 164,
      status: 'closing_soon',
      statusText: 'До 8:00',
      deliveryTime: '25 мин',
      deliveryPrice: '1500 ₸'
    },
    {
      id: 2,
      image: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=400&fit=crop',
      badgeText: 'Быстрая доставка',
      badgeColor: 'green',
      name: 'Цветочный рай',
      rating: 4.8,
      reviewsCount: 89,
      status: 'open',
      statusText: 'Открыт',
      deliveryTime: '30 мин',
      deliveryPrice: 'Бесплатно'
    }
  ];

  // Тестовые данные для отзывов о платформе (пока нет API)
  const testReviews = [
    {
      id: 1,
      authorName: 'Елена М.',
      date: '20.03.2023',
      rating: 5,
      reviewTitle: 'Отличная платформа',
      text: 'Cvety.kz - прекрасная платформа для заказа цветов. Большой выбор магазинов, удобное приложение, быстрая доставка. Особенно нравится возможность сравни...',
      likesCount: 15,
      dislikesCount: 0
    },
    {
      id: 2,
      authorName: 'Артур К.',
      date: '18.03.2023',
      rating: 5,
      reviewTitle: 'Спасли в последний момент',
      text: 'Забыл про день рождения жены, заказал букет в срочном порядке через приложение. Доставили за 40 минут! Жена была в восторге от букета.',
      likesCount: 12,
      dislikesCount: 1
    }
  ];

  // Загрузка данных из API
  const {
    data: homeData,
    isLoading,
    error
  } = useHomeProducts(null, []);

  // Извлекаем featured продукты (используем первые 2 для демо)
  const featuredProducts = homeData?.products?.slice(0, 2) || [];

  // Трансформируем API данные в формат для FeaturedProductCard
  const uiProducts = useMemo(() => {
    return featuredProducts.map(product => ({
      id: product.id,
      image: product.image,
      price: formatPrice(product.price),
      name: product.name,
      deliveryText: 'Завтра к 15:30', // TODO: Calculate from manufacturingTime
      badge: product.featured || false,  // Показать бейдж "Уже собрали" для featured
      isFavorite: false  // TODO: Integrate with favorites system
    }));
  }, [featuredProducts]);

  const handleAddToCart = (productId) => {
    console.log('Add to cart:', productId);
    addToCart(productId);
    alert(`Товар добавлен в корзину`);
  };

  const handleFavoriteToggle = (productId) => {
    console.log('Toggle favorite:', productId);
    // TODO: Implement favorites API integration
  };

  const handleProductClick = (productId) => {
    console.log('Product clicked:', productId);
    navigate(`/product/${productId}`);
  };

  const handleStoreClick = (storeId) => {
    console.log('Store clicked:', storeId);
    // TODO: Navigate to store page when implemented
    alert(`Переход в магазин ${storeId}`);
  };

  const handleShowAllStores = () => {
    console.log('Show all stores');
    // TODO: Navigate to stores list page when implemented
    alert('Показать все магазины');
  };

  const handleShowAllReviews = () => {
    console.log('Show all reviews');
    // TODO: Navigate to all reviews page when implemented
    alert('Показать все отзывы');
  };

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      {/* Header */}
      <Header cartCount={getCartCount()} />

      {/* Main Content */}
      <main className="flex-1 px-4 py-6 space-y-6">
        {/* Featured Products Section */}
        <div className="space-y-4">
          <SectionHeader
            title="Хиты продаж"
            linkText="Все акции"
            onShowAll={() => console.log('Show all featured products')}
          />

          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col gap-4">
              <div className="w-full max-w-[352px] h-[499px] bg-gray-100 animate-pulse rounded-[8px]" />
              <div className="w-full max-w-[352px] h-[499px] bg-gray-100 animate-pulse rounded-[8px]" />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-8 text-red-500">
              <p>Ошибка загрузки: {error?.message || 'Неизвестная ошибка'}</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-2 text-[#ff6666] underline"
              >
                Попробовать снова
              </button>
            </div>
          )}

          {/* Featured Cards - вертикальный список больших карточек */}
          {!isLoading && !error && (
            <div className="flex flex-col gap-4">
              {uiProducts.map(product => (
                <FeaturedProductCard
                  key={product.id}
                  image={product.image}
                  price={product.price}
                  name={product.name}
                  deliveryText={product.deliveryText}
                  badge={product.badge}
                  isFavorite={product.isFavorite}
                  onAddToCart={() => handleAddToCart(product.id)}
                  onFavoriteToggle={() => handleFavoriteToggle(product.id)}
                  onClick={() => handleProductClick(product.id)}
                />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && uiProducts.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>Нет доступных товаров</p>
            </div>
          )}
        </div>

        {/* Popular Stores Section */}
        <div className="space-y-4">
          <PopularStores
            stores={testStores}
            onShowAll={handleShowAllStores}
            onStoreClick={handleStoreClick}
          />
        </div>

        {/* Platform Reviews Section */}
        <div className="space-y-4">
          <PlatformReviewsSection
            reviews={testReviews}
            totalCount={testReviews.length}
            onShowAll={handleShowAllReviews}
            maxVisible={2}
          />
        </div>

        {/* Spacing before footer */}
        <div className="h-8" />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
