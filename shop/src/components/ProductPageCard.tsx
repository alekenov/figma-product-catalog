import { Header } from './Header';
import { ProductImageCarousel } from './ProductImageCarousel';
import { ProductInfo } from './ProductInfo';
import { ProductOptions } from './ProductOptions';
import { ProductPurchaseSection } from './ProductPurchaseSection';
import { ProductRecommendations } from './ProductRecommendations';
import { ReviewCard } from './ReviewCard';
import { MinimalFooter } from './MinimalFooter';

function ProductHeader() {
  return (
    <div className="bg-white border-b border-[var(--border)]">
      <Header />
      <div className="px-[var(--spacing-4)] py-[var(--spacing-3)]">
        <button className="flex items-center gap-2 text-[var(--text-secondary)]">
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
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-[var(--background-secondary)] min-h-screen">
        <ProductHeader />
        
        {/* Main Content */}
        <div className="space-y-[var(--spacing-4)] p-[var(--spacing-4)] pb-[var(--spacing-8)]">
          {/* Product Images - Full width */}
          <div className="relative -mx-[var(--spacing-4)] mb-[var(--spacing-2)]">
            <ProductImageCarousel />
          </div>
          
          {/* Product Info */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <ProductInfo />
          </div>
          
          {/* Product Options */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <ProductOptions />
          </div>
          
          {/* Purchase Section */}
          <ProductPurchaseSection />
          
          {/* Reviews */}
          <ReviewsSection />
          
          {/* Recommendations */}
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
            <ProductRecommendations />
          </div>
        </div>
        
        <MinimalFooter />
      </div>
    </div>
  );
}