import { CvetyQuantityControl } from './ui/cvety-quantity-control';
import { useState } from 'react';
import imgImage7 from "figma:asset/1281c56fca7983de4a0dc2a33d981cd2d80e24ff.png";
import imgImage8 from "figma:asset/7bf2958218ee8599510db937926b1c0f7cd5f07d.png";
import imgImage9 from "figma:asset/91d0f2546f3ddf10b36364d263b479db2b9c09c2.png";

interface CartItem {
  id: string;
  name: string;
  variant: string;
  price: number;
  quantity: number;
  image: string;
}

const initialCartItems: CartItem[] = [
  {
    id: '1',
    name: 'Аромобукет',
    variant: 'L / 170 000 ₸',
    price: 170000,
    quantity: 1,
    image: imgImage7
  },
  {
    id: '2', 
    name: 'Букет сухоцветов',
    variant: '15 шт / 16 000 ₸',
    price: 16000,
    quantity: 1,
    image: imgImage8
  },
  {
    id: '3',
    name: 'Букет сухоцветов',
    variant: '1 уп / 7 000 ₸',
    price: 7000,
    quantity: 1,
    image: imgImage9
  }
];

function CartItemComponent({ item, onRemove }: { item: CartItem; onRemove: (id: string) => void }) {
  const [quantity, setQuantity] = useState(item.quantity);

  return (
    <div className="flex gap-[var(--spacing-2)] items-start border-b border-[var(--border)] pb-[var(--spacing-4)]">
      <div className="relative rounded-lg shrink-0 size-14">
        <img 
          alt={item.name}
          className="absolute inset-0 max-w-none object-cover rounded-lg size-full" 
          src={item.image} 
        />
      </div>
      
      <div className="flex-1 flex items-center justify-between">
        <div>
          <h4 className="text-body-emphasis text-[var(--text-primary)] mb-1">{item.name}</h4>
          <p className="text-caption text-[var(--text-secondary)] mb-1">{item.variant}</p>
        </div>
        
        <CvetyQuantityControl 
          value={quantity}
          onDecrease={() => {
            if (quantity === 1) {
              onRemove(item.id);
            } else {
              setQuantity(q => q - 1);
            }
          }}
          onIncrease={() => setQuantity(q => q + 1)}
          showTrashIcon={true}
        />
      </div>
    </div>
  );
}

export function CartItems() {
  const [items, setItems] = useState(initialCartItems);
  
  const handleRemoveItem = (itemId: string) => {
    setItems(prevItems => prevItems.filter(item => item.id !== itemId));
  };

  return (
    <div className="space-y-[var(--spacing-3)]">
      {items.map((item) => (
        <CartItemComponent key={item.id} item={item} onRemove={handleRemoveItem} />
      ))}
      {items.length === 0 && (
        <div className="text-center py-[var(--spacing-8)]">
          <p className="text-body text-[var(--text-secondary)]">Корзина пуста</p>
        </div>
      )}
    </div>
  );
}