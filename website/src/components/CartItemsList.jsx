import React from 'react';
import QuantityControl from './ui/QuantityControl';

/**
 * CartItemsList - Cart items list from Figma (352px width)
 *
 * @param {Array} items - Array of cart items [{id, image, name, size, price, quantity}]
 * @param {function} onQuantityChange - Callback(itemId, newQuantity)
 */
export default function CartItemsList({ items = [], onQuantityChange }) {
  const handleDecrease = (itemId, currentQuantity) => {
    if (currentQuantity > 1) {
      onQuantityChange(itemId, currentQuantity - 1);
    }
  };

  const handleIncrease = (itemId, currentQuantity) => {
    onQuantityChange(itemId, currentQuantity + 1);
  };

  return (
    <div
      className="flex flex-col"
      style={{ width: '352px', gap: '12px' }}
    >
      {items.map((item) => (
        <div
          key={item.id}
          className="relative border-b border-neutral-200"
          style={{ height: '73px' }}
        >
          {/* Product Image */}
          <div
            className="absolute left-0 top-0 rounded-[12px] overflow-hidden"
            style={{ width: '56px', height: '56px' }}
          >
            <img
              src={item.image}
              alt={item.name}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Content Container */}
          <div
            className="absolute flex items-center justify-between"
            style={{
              left: '64px',
              top: 0,
              width: '288px',
              height: '56px'
            }}
          >
            {/* Product Info */}
            <div className="flex flex-col" style={{ gap: '4px' }}>
              {/* Product Name */}
              <h4
                className="font-sans font-medium"
                style={{
                  fontSize: '16px',
                  lineHeight: '24px',
                  color: 'var(--text-primary)'
                }}
              >
                {item.name}
              </h4>

              {/* Size and Price */}
              <p
                className="font-sans font-normal"
                style={{
                  fontSize: '16px',
                  lineHeight: '24px',
                  color: 'var(--text-secondary)'
                }}
              >
                {item.size} / {item.price.toLocaleString('ru-KZ')} ₸
              </p>
            </div>

            {/* Quantity Control */}
            <QuantityControl
              quantity={item.quantity}
              onDecrease={() => handleDecrease(item.id, item.quantity)}
              onIncrease={() => handleIncrease(item.id, item.quantity)}
              min={1}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
