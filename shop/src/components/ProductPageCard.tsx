import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { fetchProduct, Product } from '../services/shopApi';
import { CvetyButton } from './ui/cvety-button';
import { Header } from './Header';
import { ProductImageCarousel } from './ProductImageCarousel';
import { ProductInfo } from './ProductInfo';
import { ProductOptions } from './ProductOptions';
import { ProductPurchaseSection } from './ProductPurchaseSection';
import { ProductRecommendations } from './ProductRecommendations';
import { ReviewCard } from './ReviewCard';
import { MinimalFooter } from './MinimalFooter';

interface ProductHeaderProps {
  onBack: () => void;
  shopSlug: string;
  itemCount: number;
}

function ProductHeader({ onBack, shopSlug, itemCount }: ProductHeaderProps) {
  const navigate = useNavigate();

  const handleNavigate = (page: string, data?: any) => {
    if (page === 'cart') {
      navigate(`/${shopSlug}/cart`);
    } else if (page === 'home') {
      navigate(`/${shopSlug}`);
    }
  };
  return (
    <div className="bg-white border-b border-[var(--border)]">
      <div className="px-[var(--spacing-4)]">
        <Header onNavigate={handleNavigate} itemCount={itemCount} />
      </div>
      <div className="px-[var(--spacing-4)] py-[var(--spacing-3)]">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 4L6 8L10 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className="text-sm">Назад к каталогу</span>
        </button>
      </div>
    </div>
  );
}

function ReviewsSection() {
  const reviews = [
    {
      id: "review-1",
      author: "Елена М.",
      date: "20.03.2023",
      rating: 5,
      title: "Прекрасный букет",
      content: "Огромное спасибо за шикарный букет и самый качественный сервис. Готов рекомендовать всем знакомым и близким.",
      likes: 2,
      dislikes: 0,
      images: ["https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400"]
    },
    {
      id: "review-2", 
      author: "Артур К.",
      date: "18.03.2023",
      rating: 4,
      title: "Хорошее качество",
      content: "Заказывал букет на день рождения. Качество хорошее, доставка вовремя. Рекомендую!",
      likes: 1,
      dislikes: 0
    }
  ];

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <div className="space-y-[var(--spacing-4)]">
        <div className="flex items-center justify-between">
          <h3 className="text-[var(--text-primary)] font-medium">Отзывы (164)</h3>
          <div className="flex items-center gap-1">
            <div className="flex gap-0.5">
              {[1,2,3,4,5].map((star) => (
                <svg key={star} width="14" height="14" viewBox="0 0 14 14" fill="var(--brand-warning)">
                  <path d="M7 1L8.5 5H12.5L9.5 7.5L11 12L7 9L3 12L4.5 7.5L1.5 5H5.5L7 1Z" />
                </svg>
              ))}
            </div>
            <span className="text-sm text-[var(--text-secondary)] ml-1">4.6</span>
          </div>
        </div>
        
        <div className="space-y-[var(--spacing-3)]">
          {reviews.map((review) => (
            <ReviewCard key={review.id} {...review} />
          ))}
        </div>
        
        <button className="w-full p-[var(--spacing-3)] text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] font-medium hover:bg-[var(--brand-primary)]/5 transition-colors text-sm">
          Показать еще отзывы
        </button>
      </div>
    </div>
  );
}

export function ProductPageCard() {
  const navigate = useNavigate();
  const { shopSlug, productId } = useParams();
  const { addToCart, items, itemCount } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadProduct() {
      if (!productId) {
        setError(new Error('Product ID not provided'));
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchProduct(parseInt(productId));
        setProduct(data);
      } catch (err) {
        console.error('[ProductPageCard] Failed to load product:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }

    loadProduct();
  }, [productId]);

  const handleBack = () => {
    navigate(`/${shopSlug}`);
  };

  const handleAddToCart = () => {
    if (!product) return;

    const primaryImage = product.images.find(img => img.is_primary)?.url || product.images[0]?.url || product.image;

    addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      image: primaryImage,
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-[var(--background-secondary)] min-h-screen">
        <div className="w-full max-w-sm mx-auto">
          <ProductHeader onBack={handleBack} shopSlug={shopSlug || 'vetka'} itemCount={itemCount} />
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--brand-primary)] mx-auto mb-4"></div>
              <p className="text-[var(--text-secondary)]">Загрузка товара...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !product) {
    return (
      <div className="bg-[var(--background-secondary)] min-h-screen">
        <div className="w-full max-w-sm mx-auto">
          <ProductHeader onBack={handleBack} shopSlug={shopSlug || 'vetka'} itemCount={itemCount} />
          <div className="flex items-center justify-center h-96 px-4">
            <div className="text-center">
              <div className="text-6xl mb-4">😔</div>
              <p className="text-[var(--text-primary)] font-semibold mb-2">Товар не найден</p>
              <p className="text-[var(--text-secondary)] mb-4">
                {error?.message || 'Не удалось загрузить информацию о товаре'}
              </p>
              <CvetyButton onClick={handleBack}>
                Вернуться к каталогу
              </CvetyButton>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Get primary image
  const primaryImage = product.images.find(img => img.is_primary)?.url || product.images[0]?.url || product.image;
  const priceInTenge = Math.floor(product.price / 100);

  // Check if product is already in cart
  const cartItem = items.find(item => item.product_id === product.id);
  const isInCart = !!cartItem;
  const cartQuantity = cartItem?.quantity || 0;

  const handleCartAction = () => {
    if (isInCart) {
      // Navigate to cart if product is already added
      navigate(`/${shopSlug}/cart`);
    } else {
      // Add to cart if not added yet
      handleAddToCart();
    }
  };

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-[var(--background-secondary)] min-h-screen">
        <ProductHeader onBack={handleBack} shopSlug={shopSlug || 'vetka'} itemCount={itemCount} />

        {/* Main Content */}
        <div className="space-y-[var(--spacing-4)] p-[var(--spacing-4)] pb-[var(--spacing-8)]">
          {/* Product Image */}
          {primaryImage && (
            <div className="relative -mx-[var(--spacing-4)] mb-[var(--spacing-2)]">
              <img
                src={primaryImage}
                alt={product.name}
                className="w-full aspect-square object-cover"
              />
            </div>
          )}

          {/* Product Info Card */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
              {product.name}
            </h1>
            <div className="text-3xl font-bold text-[var(--brand-primary)] mb-4">
              {priceInTenge.toLocaleString()} ₸
            </div>

            {product.description && (
              <div className="mt-4 pt-4 border-t border-[var(--border)]">
                <h3 className="font-semibold text-[var(--text-primary)] mb-2">Описание</h3>
                <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                  {product.description}
                </p>
              </div>
            )}

            {/* Product Meta */}
            <div className="mt-4 pt-4 border-t border-[var(--border)] space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-[var(--text-secondary)]">Тип:</span>
                <span className="text-[var(--text-primary)] font-medium">{product.type}</span>
              </div>

              {product.colors && product.colors.length > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-[var(--text-secondary)]">Цвета:</span>
                  <span className="text-[var(--text-primary)]">{product.colors.join(', ')}</span>
                </div>
              )}

              {product.occasions && product.occasions.length > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-[var(--text-secondary)]">Повод:</span>
                  <span className="text-[var(--text-primary)]">{product.occasions.join(', ')}</span>
                </div>
              )}
            </div>
          </div>

          {/* Add to Cart Section */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <CvetyButton
              onClick={handleCartAction}
              className="w-full"
              size="lg"
            >
              {isInCart ? `Перейти в корзину (×${cartQuantity})` : 'Добавить в корзину'}
            </CvetyButton>
            <p className="text-xs text-center text-[var(--text-secondary)] mt-2">
              {isInCart ? 'Товар уже в корзине' : 'Товар будет добавлен в вашу корзину'}
            </p>
          </div>
        </div>

        <MinimalFooter />
      </div>
    </div>
  );
}