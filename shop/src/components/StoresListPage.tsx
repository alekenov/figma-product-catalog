import { Header } from './Header';
import { Footer } from './Footer';
import { StoreCard } from './StoreCard';
import { CvetyButton } from './ui/cvety-button';
import { CvetyInput } from './ui/cvety-input';
import { CvetyBadge } from './ui/cvety-badge';
import { useState } from 'react';
import imgImage6 from "figma:asset/3503d8004f92c1b0ba0b038933311bcedb54ff09.png";
import imgImage7 from "figma:asset/a48251912860c71257feff0c580c1fba6e724118.png";
import imgImage8 from "figma:asset/a763c5f33269c2bbd4306454e16d47682fec708c.png";

interface Store {
  id: string;
  name: string;
  rating: number;
  reviewCount: number;
  image?: string;
  isOpen: boolean;
  openTime?: string;
  deliveryTime: string;
  deliveryPrice?: number;
  badges?: string[];
}

const mockStores: Store[] = [
  {
    id: 'vetka',
    name: 'Vetka - магазин цветов',
    rating: 4.6,
    reviewCount: 164,
    image: imgImage6,
    isOpen: false,
    openTime: '8:00',
    deliveryTime: '25 мин',
    deliveryPrice: 1500,
    badges: ['Лучший рейтинг']
  },
  {
    id: 'flower-paradise',
    name: 'Цветочный рай',
    rating: 4.8,
    reviewCount: 89,
    image: imgImage7,
    isOpen: true,
    deliveryTime: '30 мин',
    badges: ['Быстрая доставка']
  },
  {
    id: 'roses-delivery',
    name: 'Доставка роз',
    rating: 4.3,
    reviewCount: 127,
    image: imgImage8,
    isOpen: true,
    deliveryTime: '45 мин',
    deliveryPrice: 2000,
    badges: ['Премиум качество']
  },
  {
    id: 'flower-house',
    name: 'Дом цветов',
    rating: 4.5,
    reviewCount: 203,
    isOpen: false,
    openTime: '9:00',
    deliveryTime: '35 мин',
    deliveryPrice: 1200
  },
  {
    id: 'bloom-express',
    name: 'Bloom Express',
    rating: 4.4,
    reviewCount: 74,
    isOpen: true,
    deliveryTime: '20 мин',
    deliveryPrice: 800,
    badges: ['Экспресс доставка']
  }
];

interface StoresListPageProps {
  onStoreSelect?: (storeId: string) => void;
}

export function StoresListPage({ onStoreSelect }: StoresListPageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'open' | 'fast'>('all');

  const filteredStores = mockStores.filter(store => {
    const matchesSearch = store.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (selectedFilter === 'open') {
      return matchesSearch && store.isOpen;
    }
    if (selectedFilter === 'fast') {
      return matchesSearch && parseInt(store.deliveryTime) <= 30;
    }
    
    return matchesSearch;
  });

  const handleStoreClick = (storeId: string) => {
    onStoreSelect?.(storeId);
  };

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
        <Header />
        
        <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-2)]">
            <h1 className="text-[var(--text-primary)] font-medium">Магазины цветов</h1>
            <p className="text-[var(--text-secondary)]">Выберите магазин для заказа букетов в Астане</p>
          </div>

          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
            <CvetyInput
              type="search"
              placeholder="Поиск магазинов..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            <div className="flex gap-[var(--spacing-2)] overflow-x-auto pb-2">
              <button
                onClick={() => setSelectedFilter('all')}
                className={`relative px-4 py-2 rounded-2xl transition-all text-sm font-medium border whitespace-nowrap flex-shrink-0 ${
                  selectedFilter === 'all'
                    ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                    : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
                }`}
              >
                Все магазины
                {selectedFilter === 'all' && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path 
                        d="M2 5L4 7L8 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                )}
              </button>
              <button
                onClick={() => setSelectedFilter('open')}
                className={`relative px-4 py-2 rounded-2xl transition-all text-sm font-medium border whitespace-nowrap flex-shrink-0 ${
                  selectedFilter === 'open'
                    ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                    : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
                }`}
              >
                Открыты сейчас
                {selectedFilter === 'open' && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path 
                        d="M2 5L4 7L8 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                )}
              </button>
              <button
                onClick={() => setSelectedFilter('fast')}
                className={`relative px-4 py-2 rounded-2xl transition-all text-sm font-medium border whitespace-nowrap flex-shrink-0 ${
                  selectedFilter === 'fast'
                    ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                    : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
                }`}
              >
                Быстрая доставка
                {selectedFilter === 'fast' && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path 
                        d="M2 5L4 7L8 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                )}
              </button>
            </div>
          </div>

          <div className="space-y-[var(--spacing-4)]">
            <div className="flex justify-between items-center">
              <p className="text-[var(--text-secondary)]">
                Найдено {filteredStores.length} магазинов
              </p>
            </div>

            <div className="space-y-[var(--spacing-4)]">
              {filteredStores.map((store) => (
                <StoreCard
                  key={store.id}
                  {...store}
                  onClick={handleStoreClick}
                />
              ))}
            </div>

            {filteredStores.length === 0 && (
              <div className="text-center py-[var(--spacing-8)]">
                <p className="text-[var(--text-secondary)]">
                  По вашему запросу магазины не найдены
                </p>
              </div>
            )}
          </div>

          <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
            <h3 className="text-[var(--text-primary)] font-medium">Популярные категории</h3>
            <div className="flex flex-wrap gap-[var(--spacing-2)]">
              <CvetyBadge variant="neutral">Розы</CvetyBadge>
              <CvetyBadge variant="neutral">Тюльпаны</CvetyBadge>
              <CvetyBadge variant="neutral">Пионы</CvetyBadge>
              <CvetyBadge variant="neutral">Букеты невесты</CvetyBadge>
              <CvetyBadge variant="neutral">Сухоцветы</CvetyBadge>
              <CvetyBadge variant="neutral">Композиции</CvetyBadge>
            </div>
          </div>
        </div>
        
        <Footer />
      </div>
    </div>
  );
}