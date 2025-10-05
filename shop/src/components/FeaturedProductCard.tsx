import svgPaths from "../imports/svg-rauipwsa5m";

function AddButton() {
  return (
    <div className="relative shrink-0 size-[32px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
        <rect fill="var(--background-muted)" height="32" rx="16" width="32" />
        <path d="M16 9.5L16 22.5M22.5 16H9.5" stroke="var(--text-primary)" />
      </svg>
    </div>
  );
}

function DeliveryInfo() {
  return (
    <div className="flex items-center gap-1">
      <div className="w-3 h-3">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 11">
          <path clipRule="evenodd" d={svgPaths.p1a1b400} fill="var(--text-secondary)" fillRule="evenodd" />
          <path clipRule="evenodd" d={svgPaths.p26c48780} fill="var(--text-secondary)" fillRule="evenodd" />
          <path clipRule="evenodd" d={svgPaths.p3374e300} fill="var(--text-secondary)" fillRule="evenodd" />
        </svg>
      </div>
      <span className="text-caption text-[var(--text-secondary)]">Завтра к 15:30</span>
    </div>
  );
}

export function FeaturedProductCard({
  images,
  title,
  price,
  isFavorite = false,
  hasPreassembledBadge = false,
  onClick
}: {
  images: string[];
  title: string;
  price: string;
  isFavorite?: boolean;
  hasPreassembledBadge?: boolean;
  onClick?: () => void;
}) {
  return (
    <div className="relative w-full col-span-2 cursor-pointer" onClick={onClick}>
      <div className="flex flex-col gap-1">
        {/* Вертикально фокусное изображение с горизонтальным слайдером */}
        <div className="relative h-96 rounded-[var(--radius-md)] overflow-hidden">
          <div className="flex h-full overflow-x-auto scroll-smooth snap-x snap-mandatory scrollbar-hide">
            {images.map((image, index) => (
              <div key={index} className="flex-none w-full h-full snap-start">
                <img 
                  alt={`${title} - изображение ${index + 1}`}
                  className="w-full h-full object-cover object-center" 
                  src={image} 
                />
              </div>
            ))}
          </div>
          
          {/* Индикаторы слайдов */}
          {images.length > 1 && (
            <div className="absolute bottom-[var(--spacing-3)] left-1/2 transform -translate-x-1/2 flex gap-1">
              {images.map((_, index) => (
                <div 
                  key={index}
                  className="w-1.5 h-1.5 rounded-full bg-white/60"
                />
              ))}
            </div>
          )}
          
          {hasPreassembledBadge && (
            <div className="absolute top-[var(--spacing-3)] left-[var(--spacing-3)] bg-[var(--brand-primary)] px-[var(--spacing-3)] py-[var(--spacing-2)] rounded-full">
              <span className="text-label text-white">Уже собрали</span>
            </div>
          )}
          
          {/* Иконка избранного в правом верхнем углу */}
          <div className="absolute top-[var(--spacing-3)] right-[var(--spacing-3)]">
            <svg 
              className={`w-6 h-6 ${isFavorite ? 'fill-[var(--brand-primary)]' : 'fill-white stroke-[var(--text-secondary)] stroke-1'}`}
              viewBox="0 0 24 24"
            >
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </div>
        </div>
        
        {/* Информация о товаре */}
        <div className="flex items-start justify-between mt-[var(--spacing-3)]">
          <div className="flex flex-col gap-1 flex-1">
            <div className="text-price text-[var(--text-primary)]">{price}</div>
            <div className="text-body text-[var(--text-primary)] leading-tight line-clamp-2">{title}</div>
          </div>
          <AddButton />
        </div>
        
        <DeliveryInfo />
      </div>
    </div>
  );
}

// Backward compatibility - создает массив из одного изображения
export function FeaturedProductCardSingle({
  image,
  title,
  price,
  isFavorite = false,
  hasPreassembledBadge = false,
  onClick
}: {
  image: string;
  title: string;
  price: string;
  isFavorite?: boolean;
  hasPreassembledBadge?: boolean;
  onClick?: () => void;
}) {
  return (
    <FeaturedProductCard
      images={[image]}
      title={title}
      price={price}
      isFavorite={isFavorite}
      hasPreassembledBadge={hasPreassembledBadge}
      onClick={onClick}
    />
  );
}