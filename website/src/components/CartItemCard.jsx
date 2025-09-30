import React from 'react';
import CvetyQuantityControl from './ui/cvety-quantity-control';

/**
 * CartItemCard - карточка товара в корзине
 *
 * @param {string} image - URL изображения товара
 * @param {string} name - Название товара
 * @param {string} size - Размер/единица измерения (например: "L", "15 шт", "1 уп")
 * @param {string} price - Цена за единицу
 * @param {number} quantity - Количество товара
 * @param {function} onIncrease - Колбэк при увеличении количества
 * @param {function} onDecrease - Колбэк при уменьшении количества
 */
export default function CartItemCard({
  image,
  name,
  size,
  price,
  quantity,
  onIncrease,
  onDecrease
}) {
  return (
    <div className="flex gap-3 items-start w-full">
      {/* Product Image - 55x55px */}
      <div className="w-[55px] h-[55px] rounded-md overflow-hidden shrink-0">
        <img
          src={image}
          alt={name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Product Info */}
      <div className="flex justify-between items-start flex-1 min-w-0">
        <div className="flex flex-col gap-1">
          {/* Product Name */}
          <div className="font-sans font-normal text-body-2 text-text-black">
            {name}
          </div>

          {/* Size and Price */}
          <div className="flex items-center gap-1 font-sans font-normal text-field-title text-text-grey-dark">
            <span>{size}</span>
            <span>•</span>
            <span>{price}</span>
          </div>
        </div>

        {/* Quantity Controls */}
        <CvetyQuantityControl
          value={quantity}
          onDecrease={onDecrease}
          onIncrease={onIncrease}
          min={1}
          max={99}
        />
      </div>
    </div>
  );
}