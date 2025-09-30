import React from 'react';

/**
 * OrderLineItems - детальная разбивка заказа с товарами и итогом
 *
 * @param {Array} items - Массив товаров [{name, price}]
 * @param {number} deliveryCost - Стоимость доставки
 * @param {string} deliveryType - Тип доставки (например "Самовывоз")
 * @param {number} total - Общая стоимость
 * @param {number} bonusPoints - Бонусные баллы за заказ
 * @param {string} currency - Валюта (по умолчанию ₸)
 */
export default function OrderLineItems({
  items = [],
  deliveryCost = 0,
  deliveryType = 'Доставка',
  total = 0,
  bonusPoints = 0,
  currency = '₸'
}) {
  const formatPrice = (price) => {
    return `${price.toLocaleString('ru-RU')} ${currency}`;
  };

  return (
    <div className="space-y-4">
      {/* Line Items */}
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="flex justify-between items-start">
            <span className="font-sans font-normal text-[14px] leading-[1.3] text-text-black flex-1">
              {item.name}
            </span>
            <span className="font-sans font-normal text-[16px] leading-[1.3] text-text-black ml-4">
              {formatPrice(item.price)}
            </span>
          </div>
        ))}
      </div>

      {/* Delivery */}
      <div className="flex justify-between items-center pt-3 border-t border-[var(--bg-tertiary)]">
        <span className="font-sans font-normal text-[14px] leading-[1.3] text-text-black">
          {deliveryType}
        </span>
        <span className="font-sans font-normal text-[16px] leading-[1.3] text-text-black">
          {formatPrice(deliveryCost)}
        </span>
      </div>

      {/* Total Section */}
      <div className="pt-3 border-t border-[var(--bg-tertiary)] space-y-2">
        <div className="flex justify-between items-center">
          <span className="font-sans font-normal text-[14px] leading-[1.3] text-text-black">
            Общая стоимость:
          </span>
          <span className="font-sans font-semibold text-[16px] leading-[1.3] text-text-black">
            {formatPrice(total)}
          </span>
        </div>

        {/* Bonus Points */}
        {bonusPoints > 0 && (
          <p className="font-sans font-normal text-[14px] leading-[1.2] text-text-grey-dark">
            +{bonusPoints} баллов на следующий заказ
          </p>
        )}
      </div>
    </div>
  );
}