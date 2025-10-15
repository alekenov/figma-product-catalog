import { CvetyQuantityControl } from './ui/cvety-quantity-control';
import { useCart, CartItem } from '../contexts/CartContext';

function CartItemComponent({ item, onDecrease, onIncrease, onRemove }: {
  item: CartItem;
  onDecrease: () => void;
  onIncrease: () => void;
  onRemove: () => void;
}) {
  // Format price from kopecks to tenge
  const priceInTenge = Math.floor(item.product_price / 100);

  return (
    <div className="flex gap-[var(--spacing-2)] items-start border-b border-[var(--border)] pb-[var(--spacing-4)]">
      {/* Product Image */}
      <div className="relative rounded-lg shrink-0 size-14 bg-gray-100">
        {item.image ? (
          <img
            alt={item.product_name}
            className="absolute inset-0 max-w-none object-cover rounded-lg size-full"
            src={item.image}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      <div className="flex-1 flex items-center justify-between">
        <div>
          <h4 className="text-body-emphasis text-[var(--text-primary)] mb-1">{item.product_name}</h4>
          <p className="text-caption text-[var(--text-secondary)] mb-1">
            {priceInTenge.toLocaleString()} ₸
          </p>
        </div>

        <CvetyQuantityControl
          value={item.quantity}
          onDecrease={onDecrease}
          onIncrease={onIncrease}
          showTrashIcon={true}
        />
      </div>
    </div>
  );
}

export function CartItems() {
  const { items, updateQuantity, removeFromCart } = useCart();

  const handleDecrease = (productId: number, currentQuantity: number) => {
    if (currentQuantity === 1) {
      removeFromCart(productId);
    } else {
      updateQuantity(productId, currentQuantity - 1);
    }
  };

  return (
    <div className="space-y-[var(--spacing-3)]">
      {items.map((item) => (
        <CartItemComponent
          key={item.product_id}
          item={item}
          onDecrease={() => handleDecrease(item.product_id, item.quantity)}
          onIncrease={() => updateQuantity(item.product_id, item.quantity + 1)}
          onRemove={() => removeFromCart(item.product_id)}
        />
      ))}
      {items.length === 0 && (
        <div className="text-center py-[var(--spacing-8)]">
          <p className="text-body text-[var(--text-secondary)]">Корзина пуста</p>
        </div>
      )}
    </div>
  );
}