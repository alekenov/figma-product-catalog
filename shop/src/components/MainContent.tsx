import { useState, useEffect } from 'react';
import svgPaths from "../imports/svg-rauipwsa5m";
import { ProductGrid } from './ProductGrid';
import { StoreCard } from './StoreCard';
import { FeaturedProductCard } from './FeaturedProductCard';
import { CvetyButton } from './ui/cvety-button';
import { CvetyBadge } from './ui/cvety-badge';
import { ReviewsList } from './ReviewCard';
import marketplaceApi, { Shop, Product, Review, formatPrice } from '../services/api';
import imgImage6 from "figma:asset/3503d8004f92c1b0ba0b038933311bcedb54ff09.png";
import imgImage7 from "figma:asset/a48251912860c71257feff0c580c1fba6e724118.png";

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface MainContentProps {
  onNavigate: (page: PageType, data?: { storeId?: string; productId?: string }) => void;
}

function MainTitle() {
  return (
    <h1 className="text-headline text-[var(--text-primary)]">
      Доставка цветов в Астане
    </h1>
  );
}

function ProductCountButton() {
  return (
    <CvetyButton variant="primary" size="sm" className="rounded-full">
      <span>1644 товара</span>
      <div className="w-6 h-6">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
          <path d={svgPaths.p1fcb21c0} stroke="currentColor" />
        </svg>
      </div>
    </CvetyButton>
  );
}

function FilterButton() {
  return (
    <CvetyButton variant="secondary" size="sm" className="rounded-full">
      <span>Фильтры</span>
      <div className="w-5 h-5">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
          <path d={svgPaths.p2a30280} stroke="currentColor" />
        </svg>
      </div>
    </CvetyButton>
  );
}

function FilterControls() {
  return (
    <div className="flex gap-[var(--spacing-4)] items-start">
      <ProductCountButton />
      <FilterButton />
    </div>
  );
}

function UrgentTag() {
  return (
    <CvetyBadge variant="warning" className="flex items-center gap-1 h-8 px-3 py-1 rounded-full">
      <div className="w-2 h-3.5">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 14">
          <path d={svgPaths.p19d9e300} fill="currentColor" />
        </svg>
      </div>
      <span className="whitespace-nowrap">Срочно</span>
    </CvetyBadge>
  );
}

function BudgetTag() {
  return (
    <CvetyBadge variant="success" className="flex items-center gap-1 h-8 px-3 py-1 rounded-full">
      <div className="w-3.5 h-3.5">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 14 13">
          <path d={svgPaths.p16acdc00} fill="currentColor" />
        </svg>
      </div>
      <span className="whitespace-nowrap">Бюджетные</span>
    </CvetyBadge>
  );
}

function FilterTag({ label }: { label: string }) {
  return (
    <CvetyBadge variant="neutral" className="h-8 px-3 py-1 rounded-full">
      <span className="whitespace-nowrap">{label}</span>
    </CvetyBadge>
  );
}

function FilterTags() {
  return (
    <div />
  );
}

function BestsellerTitle() {
  return (
    <h2 className="text-title text-[var(--brand-primary)]">
      Букеты-бестселлеры
    </h2>
  );
}

function PopularStores({ onNavigate }: { onNavigate: MainContentProps['onNavigate'] }) {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadShops() {
      try {
        const data = await marketplaceApi.shops.list({ limit: 5 });
        setShops(data);
      } catch (error) {
        console.error('Failed to load shops:', error);
      } finally {
        setLoading(false);
      }
    }
    loadShops();
  }, []);

  if (loading) {
    return (
      <div className="space-y-[var(--spacing-4)]">
        <h2 className="text-title text-[var(--text-primary)]">Популярные магазины</h2>
        <div className="text-center py-8 text-[var(--text-secondary)]">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="space-y-[var(--spacing-4)]">
      <div className="flex justify-between items-center">
        <h2 className="text-title text-[var(--text-primary)]">Популярные магазины</h2>
        <CvetyButton
          variant="ghost"
          size="sm"
          onClick={() => onNavigate('stores-list')}
        >
          Все магазины
        </CvetyButton>
      </div>
      <div className="space-y-[var(--spacing-3)]">
        {shops.map((shop) => (
          <StoreCard
            key={shop.id}
            id={shop.id.toString()}
            name={shop.name}
            rating={shop.rating || 0}
            reviewCount={shop.review_count || 0}
            image={imgImage6} // TODO: Use shop image when available
            isOpen={shop.is_open || false}
            deliveryTime="30 мин" // TODO: Calculate from shop data
            deliveryPrice={formatPrice(shop.delivery_cost_tenge)}
            badges={shop.rating && shop.rating >= 4.5 ? ['Лучший рейтинг'] : []}
            onClick={(storeId) => onNavigate('store', { storeId })}
          />
        ))}
      </div>
    </div>
  );
}

function FeaturedProducts({ onNavigate }: { onNavigate: MainContentProps['onNavigate'] }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFeaturedProducts() {
      try {
        const data = await marketplaceApi.products.featured({ limit: 5 });
        setProducts(data);
      } catch (error) {
        console.error('Failed to load featured products:', error);
      } finally {
        setLoading(false);
      }
    }
    loadFeaturedProducts();
  }, []);

  if (loading) {
    return (
      <div className="space-y-[var(--spacing-4)]">
        <h2 className="text-title text-[var(--brand-primary)]">Хиты продаж</h2>
        <div className="text-center py-8 text-[var(--text-secondary)]">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="space-y-[var(--spacing-4)]">
      <div className="flex justify-between items-center">
        <h2 className="text-title text-[var(--brand-primary)]">Хиты продаж</h2>
        <CvetyButton
          variant="ghost"
          size="sm"
          onClick={() => onNavigate('product')}
        >
          Все акции
        </CvetyButton>
      </div>

      <div className="space-y-[var(--spacing-4)]">
        {products.map((product) => (
          <FeaturedProductCard
            key={product.id}
            images={product.image ? [product.image] : []}
            title={product.name}
            price={formatPrice(product.price)}
            isFavorite={false} // TODO: Add favorites functionality
            hasPreassembledBadge={product.is_featured}
            onClick={() => onNavigate('product', { productId: product.id.toString() })}
          />
        ))}
      </div>
    </div>
  );
}

function CustomerReviews() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReviews() {
      try {
        const data = await marketplaceApi.reviews.platform({ limit: 3 });
        // Transform API reviews to match ReviewsList expected format
        const transformedReviews = data.reviews.map((review) => ({
          id: `review-${review.id}`,
          author: review.author_name,
          date: new Date(review.created_at).toLocaleDateString('ru-RU'),
          rating: review.rating,
          title: review.shop_name || '',
          content: review.text,
          likes: review.likes,
          dislikes: review.dislikes,
        }));
        setReviews(transformedReviews);
      } catch (error) {
        console.error('Failed to load reviews:', error);
      } finally {
        setLoading(false);
      }
    }
    loadReviews();
  }, []);

  if (loading) {
    return (
      <div className="space-y-[var(--spacing-4)]">
        <h2 className="text-title text-[var(--text-primary)]">Отзывы покупателей</h2>
        <div className="text-center py-8 text-[var(--text-secondary)]">Загрузка...</div>
      </div>
    );
  }

  return (
    <ReviewsList
      reviews={reviews}
      title="Отзывы покупателей"
      compact={true}
      maxItems={2}
    />
  );
}

export function MainContent({ onNavigate }: MainContentProps) {
  return (
    <div className="space-y-[var(--spacing-8)]">
      <MainTitle />
      <div className="space-y-[var(--spacing-4)]">
        <FilterControls />
        <FilterTags />
      </div>
      <FeaturedProducts onNavigate={onNavigate} />
      <div className="space-y-[var(--spacing-2)]">
        <BestsellerTitle />
        <ProductGrid onNavigate={onNavigate} />
      </div>
      <PopularStores onNavigate={onNavigate} />
      <CustomerReviews />
    </div>
  );
}