import { useState, useEffect } from 'react';
import { ProductCard } from './ProductCard';
import marketplaceApi, { Product, formatPrice } from '../services/api';
import imgImage6 from "figma:asset/b41712e9f9a73c76cc59bd6d3d6139fd0537c358.png";

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface ProductGridProps {
  onNavigate: (page: PageType, data?: { storeId?: string; productId?: string }) => void;
}

export function ProductGrid({ onNavigate }: ProductGridProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadBestsellers() {
      try {
        const data = await marketplaceApi.products.bestsellers(4);
        setProducts(data);
      } catch (error) {
        console.error('Failed to load bestsellers:', error);
      } finally {
        setLoading(false);
      }
    }
    loadBestsellers();
  }, []);

  if (loading) {
    return (
      <div className="text-center py-8 text-[var(--text-secondary)]">
        Загрузка...
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-8 text-[var(--text-secondary)]">
        Товары не найдены
      </div>
    );
  }

  // Split products into rows of 2
  const rows = [];
  for (let i = 0; i < products.length; i += 2) {
    rows.push(products.slice(i, i + 2));
  }

  return (
    <div className="space-y-4">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="grid grid-cols-2 gap-2">
          {row.map((product) => (
            <ProductCard
              key={product.id}
              image={product.image || imgImage6}
              title={product.name}
              price={formatPrice(product.price)}
              isFavorite={false} // TODO: Add favorites functionality
              hasPreassembledBadge={product.is_featured}
              onClick={() => onNavigate('product', { productId: product.id.toString() })}
            />
          ))}
        </div>
      ))}
    </div>
  );
}