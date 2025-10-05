import { useState } from 'react';
import imgImage7 from "figma:asset/b41712e9f9a73c76cc59bd6d3d6139fd0537c358.png";

interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  price: number;
  image: string;
  shop: string;
}

interface OrderItemsProps {
  canEdit?: boolean;
}

export function OrderItems({ canEdit = true }: OrderItemsProps) {
  const [isEditingItems, setIsEditingItems] = useState(false);
  const [items, setItems] = useState<OrderItem[]>([
    {
      id: '1',
      name: 'Букет розовых пионов',
      quantity: 1,
      price: 6900,
      shop: 'Vetka Flowers',
      image: imgImage7
    }
  ]);

  const handleQuantityChange = (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    setItems(items.map(item => 
      item.id === itemId ? { ...item, quantity: newQuantity } : item
    ));
  };

  const removeItem = (itemId: string) => {
    setItems(items.filter(item => item.id !== itemId));
  };

  const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <div className="flex items-center justify-between">
        <h2 className="text-[var(--text-primary)] font-medium">Товары в заказе</h2>
        
        {canEdit && (
          <button
            onClick={() => setIsEditingItems(!isEditingItems)}
            className="px-3 py-1 text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] text-sm font-medium hover:bg-[var(--brand-primary)]/5 transition-colors"
          >
            {isEditingItems ? 'Готово' : 'Изменить'}
          </button>
        )}
      </div>

      {!canEdit && (
        <div className="p-[var(--spacing-3)] bg-[var(--background-secondary)] rounded-[var(--radius-md)]">
          <p className="text-[var(--text-secondary)] text-sm">
            📦 Товары нельзя изменить - заказ уже передан курьеру
          </p>
        </div>
      )}
      
      <div className="space-y-[var(--spacing-3)]">
        {items.map((item) => (
          <div key={item.id} className="flex gap-[var(--spacing-3)] items-start">
            <div className="relative rounded-lg shrink-0 size-16">
              <img 
                alt={item.name}
                className="absolute inset-0 max-w-none object-cover rounded-lg size-full" 
                src={item.image} 
              />
            </div>
            
            <div className="flex-1 space-y-[var(--spacing-1)]">
              <h4 className="text-[var(--text-primary)] font-medium">
                {item.name}
              </h4>
              <div className="text-[var(--text-secondary)]">
                {!isEditingItems ? (
                  `${item.quantity} шт • ${item.shop}`
                ) : (
                  <div className="flex items-center gap-2">
                    <span>Количество:</span>
                    <div className="flex items-center gap-1 bg-[var(--background-secondary)] rounded-[var(--radius-md)] px-2 py-1">
                      <button
                        onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                        className="w-6 h-6 flex items-center justify-center text-[var(--text-primary)] hover:bg-white rounded-full transition-colors"
                        disabled={item.quantity <= 1}
                      >
                        −
                      </button>
                      <span className="min-w-[2ch] text-center text-[var(--text-primary)] font-medium">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                        className="w-6 h-6 flex items-center justify-center text-[var(--text-primary)] hover:bg-white rounded-full transition-colors"
                      >
                        +
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <div className="flex items-center justify-between">
                <p className="text-[var(--brand-primary)] font-medium">
                  {item.price.toLocaleString()} ₸
                </p>
                
                {isEditingItems && items.length > 1 && (
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-[var(--brand-error)] text-sm hover:underline"
                  >
                    Удалить
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Итоговая сумма */}
      <div className="pt-[var(--spacing-3)] border-t border-[var(--border)]">
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-primary)] font-medium">
            Итого: {items.reduce((sum, item) => sum + item.quantity, 0)} товар(ов)
          </span>
          <span className="text-[var(--brand-primary)] font-medium text-lg">
            {totalAmount.toLocaleString()} ₸
          </span>
        </div>
      </div>

      {/* Действия при редактировании */}
      {isEditingItems && (
        <div className="space-y-[var(--spacing-3)]">
          <button className="w-full px-4 py-2 border border-[var(--border)] text-[var(--text-primary)] rounded-[var(--radius-md)] font-medium hover:bg-[var(--background-secondary)] transition-colors">
            + Добавить товар
          </button>
          
          <div className="p-[var(--spacing-3)] bg-[var(--brand-warning)]/10 border border-[var(--brand-warning)]/20 rounded-[var(--radius-md)]">
            <p className="text-[var(--brand-warning)] text-sm">
              ⚠️ Внимание: изменение товаров может повлиять на стоимость доставки
            </p>
          </div>
        </div>
      )}
    </div>
  );
}