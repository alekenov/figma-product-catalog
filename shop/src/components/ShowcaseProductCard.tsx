import svgPaths from "../imports/svg-rauipwsa5m";

function QuickBuyButton() {
  return (
    <button className="px-[var(--spacing-4)] py-[var(--spacing-2)] bg-[var(--brand-primary)] text-white rounded-[var(--radius-md)] font-medium text-sm transition-all hover:bg-[var(--brand-primary-dark)] active:scale-95">
      Купить
    </button>
  );
}

function UniqueBadge() {
  return (
    <div className="inline-flex items-center gap-1 px-[var(--spacing-2)] py-[var(--spacing-1)] bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-full">
      <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
      <span className="text-xs font-medium text-amber-700">Только 1 шт</span>
    </div>
  );
}

function FloristSignature({ floristName }: { floristName: string }) {
  return (
    <div className="flex items-center gap-1 text-xs text-[var(--text-secondary)]">
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path 
          d="M6 1L7.5 4.5L11 4.5L8.25 6.75L9.75 10.25L6 8L2.25 10.25L3.75 6.75L1 4.5L4.5 4.5L6 1Z" 
          fill="var(--brand-primary)" 
        />
      </svg>
      <span>Флорист {floristName}</span>
    </div>
  );
}

export function ShowcaseProductCard({ 
  image, 
  title, 
  price, 
  floristName,
  isFavorite = false 
}: { 
  image: string; 
  title: string; 
  price: string; 
  floristName: string;
  isFavorite?: boolean;
}) {
  return (
    <div className="relative w-full">
      <div className="flex gap-[var(--spacing-3)] p-[var(--spacing-3)] bg-white rounded-[var(--radius-md)] border border-[var(--border)] hover:shadow-sm transition-all">
        {/* Увеличенное изображение с фокусом на цветы */}
        <div className="relative w-24 h-24 rounded-[var(--radius-md)] overflow-hidden flex-shrink-0">
          <img 
            alt={title}
            className="w-full h-full object-cover" 
            src={image} 
          />
          
          {/* Иконка избранного */}
          <div className="absolute top-1 right-1">
            <svg 
              className={`w-4 h-4 ${isFavorite ? 'fill-[var(--brand-primary)]' : 'fill-white stroke-[var(--text-secondary)] stroke-1'}`}
              viewBox="0 0 24 24"
            >
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </div>
        </div>
        
        {/* Информация о товаре */}
        <div className="flex-1 flex flex-col justify-between min-w-0">
          <div className="space-y-2">
            {/* Бейдж уникальности */}
            <UniqueBadge />
            
            {/* Название и цена */}
            <div className="space-y-1">
              <h3 className="font-medium text-[var(--text-primary)] text-sm leading-tight line-clamp-2">
                {title}
              </h3>
              <div className="font-bold text-[var(--text-primary)]">
                {price}
              </div>
            </div>
          </div>
          
          {/* Простая кнопка добавления */}
          <div className="flex justify-end mt-[var(--spacing-2)]">
            <button className="w-8 h-8 bg-[var(--brand-primary)] text-white rounded-full flex items-center justify-center transition-all hover:bg-[var(--brand-primary-dark)] active:scale-95">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M8 3V13M3 8H13" 
                  stroke="white" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Компонент для списка витринных товаров
export function ShowcaseGrid({ 
  title = "Витрина флориста",
  subtitle = "Уникальные букеты в единственном экземпляре",
  products 
}: {
  title?: string;
  subtitle?: string;
  products: Array<{
    id: string;
    image: string;
    title: string;
    price: string;
    floristName: string;
    isFavorite?: boolean;
  }>;
}) {
  return (
    <div className="space-y-[var(--spacing-4)]">
      {/* Заголовок секции */}
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold text-[var(--text-primary)]">{title}</h2>
          <div className="w-2 h-2 bg-[var(--brand-primary)] rounded-full animate-pulse" />
        </div>
        <p className="text-sm text-[var(--text-secondary)]">{subtitle}</p>
      </div>
      
      {/* Сетка товаров */}
      <div className="space-y-[var(--spacing-2)]">
        {products.map((product) => (
          <ShowcaseProductCard
            key={product.id}
            image={product.image}
            title={product.title}
            price={product.price}
            floristName={product.floristName}
            isFavorite={product.isFavorite}
          />
        ))}
      </div>
    </div>
  );
}