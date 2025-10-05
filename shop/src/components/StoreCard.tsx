import { CvetyBadge } from './ui/cvety-badge';

interface StoreCardProps {
  id: string;
  name: string;
  rating: number;
  reviewCount: number;
  image?: string;
  isOpen: boolean;
  openTime?: string;
  deliveryTime: string;
  deliveryPrice?: string; // Already formatted with ₸ symbol
  badges?: string[];
  onClick?: (storeId: string) => void;
}

export function StoreCard({
  id,
  name,
  rating,
  reviewCount,
  image,
  isOpen,
  openTime,
  deliveryTime,
  deliveryPrice,
  badges = [],
  onClick
}: StoreCardProps) {
  return (
    <div 
      className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] cursor-pointer hover:shadow-sm transition-shadow"
      onClick={() => onClick?.(id)}
    >
      {image && (
        <div className="h-32 relative overflow-hidden rounded-[var(--radius-md)] mb-[var(--spacing-3)]">
          <img
            src={image}
            alt={name}
            className="w-full h-full object-cover"
          />
          {badges.length > 0 && (
            <div className="absolute top-2 left-2 flex gap-1">
              {badges.map((badge, index) => (
                <CvetyBadge key={index} variant="success" className="text-micro">
                  {badge}
                </CvetyBadge>
              ))}
            </div>
          )}
        </div>
      )}
      
      <div className="space-y-[var(--spacing-2)]">
        <div className="flex justify-between items-start">
          <h3 className="text-subtitle text-[var(--text-primary)] flex-1 pr-2 line-clamp-1">{name}</h3>
          <div className="flex items-center gap-1 shrink-0">
            <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
              <path d="M7.52235 2.8769C7.66766 2.40731 8.33234 2.40731 8.47765 2.8769L9.38778 5.81802C9.45258 6.02743 9.64622 6.17021 9.86543 6.17021H12.8606C13.339 6.17021 13.5442 6.77756 13.1639 7.06774L10.6994 8.94779C10.5327 9.075 10.463 9.29277 10.525 9.49313L11.4564 12.5028C11.6002 12.9677 11.0624 13.3433 10.6754 13.0481L8.30326 11.2384C8.12417 11.1018 7.87583 11.1018 7.69674 11.2384L5.32457 13.0481C4.93758 13.3433 4.39976 12.9677 4.54365 12.5028L5.47497 9.49313C5.53697 9.29277 5.46734 9.075 5.30058 8.94779L2.83614 7.06774C2.45576 6.77756 2.66097 6.17021 3.13941 6.17021H6.13457C6.35378 6.17021 6.54742 6.02743 6.61223 5.81802L7.52235 2.8769Z" fill="var(--brand-warning)" />
            </svg>
            <span className="text-body-emphasis text-[var(--text-primary)]">{rating}</span>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-caption text-[var(--text-secondary)]">{reviewCount} отзывов</span>
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${isOpen ? 'bg-[var(--brand-success)]' : 'bg-[var(--brand-error)]'}`} />
            <span className={`text-caption ${isOpen ? 'text-[var(--brand-success)]' : 'text-[var(--brand-error)]'}`}>
              {isOpen ? 'Открыт' : (openTime ? `До ${openTime}` : 'Закрыт')}
            </span>
          </div>
        </div>
        
        <div className="flex justify-between items-center pt-1 border-t border-[var(--border)]">
          <span className="text-caption text-[var(--text-secondary)]">Доставка {deliveryTime}</span>
          {deliveryPrice ? (
            <span className="text-body-emphasis text-[var(--text-primary)]">{deliveryPrice}</span>
          ) : (
            <span className="text-body-emphasis text-[var(--brand-success)]">Бесплатно</span>
          )}
        </div>
      </div>
    </div>
  );
}