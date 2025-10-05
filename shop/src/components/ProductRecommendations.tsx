import { ProductCard } from './ProductCard';

const recommendedProducts = [
  {
    id: '1',
    image: 'https://images.unsplash.com/photo-1520763185298-1b434c919102?w=400',
    title: 'Букет белых роз',
    price: '18 900 ₸',
    isFavorite: false,
    hasPreassembledBadge: true
  },
  {
    id: '2',
    image: 'https://images.unsplash.com/photo-1542080681-2ec8ab607ad4?w=400',
    title: 'Букет тюльпанов',
    price: '8 900 ₸',
    isFavorite: true,
    hasPreassembledBadge: false
  },
  {
    id: '3',
    image: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400',
    title: 'Букет хризантем',
    price: '10 900 ₸',
    isFavorite: false,
    hasPreassembledBadge: false
  }
];

export function ProductRecommendations() {
  return (
    <div className="space-y-[var(--spacing-4)]">
      <h3 className="text-[var(--text-primary)] font-medium">Рекомендуемые товары</h3>
      
      <div className="flex gap-[var(--spacing-3)] overflow-x-auto pb-2 -mx-[var(--spacing-4)] px-[var(--spacing-4)]">
        {recommendedProducts.map((product) => (
          <div key={product.id} className="flex-shrink-0">
            <ProductCard {...product} />
          </div>
        ))}
      </div>
    </div>
  );
}