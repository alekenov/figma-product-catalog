import { ProductCard } from './ProductCard';
import { FeaturedProductCard } from './FeaturedProductCard';
import imgImage6 from "figma:asset/3503d8004f92c1b0ba0b038933311bcedb54ff09.png";
import imgImage7 from "figma:asset/a48251912860c71257feff0c580c1fba6e724118.png";
import imgImage8 from "figma:asset/a763c5f33269c2bbd4306454e16d47682fec708c.png";
import imgImage9 from "figma:asset/b748a97358f8796661d37dc271698d7380f38499.png";

export function StoreProducts() {
  const storeFeatured = {
    images: [
      'https://images.unsplash.com/photo-1662326495491-764da874b01f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmbG9yaXN0JTIwYmVzdCUyMHNlbGxlciUyMGJvdXF1ZXR8ZW58MXx8fHwxNzU5Mzg5MzYzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      imgImage6,
      imgImage7
    ],
    title: 'Хит продаж Vetka - "Романтическое настроение" с бесплатной доставкой',
    price: '9 800 ₸',
    isFavorite: true,
    hasPreassembledBadge: true
  };

  const products = [
    {
      id: 'product-1',
      image: imgImage6,
      title: 'Букет \"Весенняя радость\"',
      price: 8500,
      oldPrice: 10000,
      discount: 15,
      rating: 4.8,
      reviewCount: 24,
      shop: 'Vetka'
    },
    {
      id: 'product-2',
      image: imgImage7,
      title: 'Розы \"Классика\"',
      price: 12000,
      rating: 4.9,
      reviewCount: 18,
      shop: 'Vetka'
    },
    {
      id: 'product-3',
      image: imgImage8,
      title: 'Букет тюльпанов',
      price: 5500,
      rating: 4.7,
      reviewCount: 31,
      shop: 'Vetka'
    },
    {
      id: 'product-4',
      image: imgImage9,
      title: 'Микс \"Нежность\"',
      price: 7200,
      oldPrice: 8000,
      discount: 10,
      rating: 4.6,
      reviewCount: 15,
      shop: 'Vetka'
    }
  ];

  return (
    <div className="space-y-[var(--spacing-6)]">
      {/* Featured товар магазина */}
      <div className="space-y-[var(--spacing-3)]">
        <div className="flex justify-between items-center">
          <h2 className="text-title text-[var(--brand-primary)]">Хит магазина</h2>
        </div>
        <FeaturedProductCard {...storeFeatured} />
      </div>
      
      {/* Основные товары */}
      <div className="space-y-[var(--spacing-4)]">
        <div className="flex justify-between items-center">
          <h2 className="text-title text-[var(--text-primary)]">Товары (84)</h2>
          <button className="text-caption text-[var(--brand-primary)]">
            Сортировка
          </button>
        </div>
        
        <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              {...product}
              price={`${product.price.toLocaleString('ru-KZ')} ₸`}
            />
          ))}
        </div>
        
        <button className="w-full p-[var(--spacing-3)] text-button text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] hover:bg-[var(--brand-primary)]/5 transition-colors">
          Показать еще товары
        </button>
      </div>
    </div>
  );
}