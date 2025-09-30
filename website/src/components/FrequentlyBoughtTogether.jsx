import React, { useState } from 'react';

/**
 * FrequentlyBoughtTogether - секция "С этим товаром часто покупают"
 *
 * @param {Array} products - Массив рекомендуемых товаров [{id, name, price, image}]
 * @param {function} onProductToggle - Колбэк при добавлении/удалении товара
 */
export default function FrequentlyBoughtTogether({ products, onProductToggle }) {
  const [selectedProducts, setSelectedProducts] = useState([]);

  const handleToggle = (productId) => {
    const newSelected = selectedProducts.includes(productId)
      ? selectedProducts.filter(id => id !== productId)
      : [...selectedProducts, productId];

    setSelectedProducts(newSelected);
    onProductToggle?.(newSelected);
  };

  // Подсчет общей суммы
  const totalPrice = products
    .filter(p => selectedProducts.includes(p.id))
    .reduce((sum, p) => sum + parseFloat(p.price.replace(/[^\d]/g, '')), 0);

  const selectedItems = products.filter(p => selectedProducts.includes(p.id));

  return (
    <div className="space-y-4">
      {/* Section Title */}
      <h3 className="font-sans font-bold text-h3 text-text-black">
        С этим товаром часто покупают
      </h3>

      {/* Products Grid */}
      <div className="grid grid-cols-3 gap-3">
        {products.map((product) => (
          <div key={product.id} className="space-y-2">
            {/* Product Image */}
            <div className="relative w-full aspect-square rounded-lg overflow-hidden bg-bg-light">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
              />

              {/* Add Button Overlay */}
              <button
                onClick={() => handleToggle(product.id)}
                className={`absolute bottom-2 right-2 w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                  selectedProducts.includes(product.id)
                    ? 'bg-pink text-white'
                    : 'bg-white text-text-black hover:bg-bg-extra-light'
                }`}
              >
                {selectedProducts.includes(product.id) ? (
                  <svg viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 13 13" fill="none" className="w-3 h-3">
                    <path
                      d="M6.5 1V12M1 6.5H12"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                )}
              </button>
            </div>

            {/* Product Info */}
            <div className="space-y-0.5">
              <div className="font-sans font-bold text-body-2 text-text-black">
                {product.price}
              </div>
              <div className="font-sans font-normal text-field-title text-text-black line-clamp-2">
                {product.name}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary (если есть выбранные товары) */}
      {selectedItems.length > 0 && (
        <div className="bg-bg-light rounded-lg p-4 space-y-2">
          {/* Item Breakdown */}
          {selectedItems.map((item) => (
            <div key={item.id} className="flex justify-between items-center">
              <span className="font-sans font-normal text-body-2 text-text-black">
                {item.name}
              </span>
              <span className="font-sans font-normal text-body-2 text-text-black">
                {item.price}
              </span>
            </div>
          ))}

          {/* Divider */}
          <div className="border-t border-bg-extra-light pt-2">
            {/* Total */}
            <div className="flex justify-between items-center">
              <span className="font-sans font-bold text-body-1 text-text-black">
                Итого:
              </span>
              <span className="font-sans font-bold text-h3 text-pink">
                {totalPrice.toLocaleString()} ₸
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}