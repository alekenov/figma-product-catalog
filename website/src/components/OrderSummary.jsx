import React from 'react';
import CvetyButton from './ui/CvetyButton';
import CvetyToggle from './ui/cvety-toggle';
import { CvetyCard, CvetyCardContent, CvetyCardHeader, CvetyCardTitle } from './ui/cvety-card';

/**
 * OrderSummary - сводка заказа с расчетом суммы
 *
 * @param {number} itemsTotal - Сумма товаров
 * @param {number} deliveryCost - Стоимость доставки
 * @param {number} promoDiscount - Скидка по промокоду (бонусы)
 * @param {boolean} usePromo - Использовать ли промокод
 * @param {function} onPromoToggle - Колбэк при переключении промокода
 * @param {string} currency - Валюта (по умолчанию ₸)
 */
export default function OrderSummary({
  itemsTotal,
  deliveryCost,
  promoDiscount = 0,
  usePromo = false,
  onPromoToggle,
  currency = '₸'
}) {
  const total = itemsTotal + deliveryCost - (usePromo ? promoDiscount : 0);

  const formatPrice = (price) => {
    return `${price.toLocaleString('ru-RU')} ${currency}`;
  };

  return (
    <CvetyCard>
      <CvetyCardHeader>
        <CvetyCardTitle className="!text-body-1 !font-semibold text-text-black">
          Ваш заказ
        </CvetyCardTitle>
      </CvetyCardHeader>

      {/* Summary Lines */}
      <CvetyCardContent className="space-y-4">
        {/* Items Total */}
        <div className="flex justify-between items-center">
          <span className="font-sans font-normal text-body-2 text-text-grey-dark">
            Товары на сумму
          </span>
          <span className="font-sans font-normal text-body-2 text-text-black">
            {formatPrice(itemsTotal)}
          </span>
        </div>

        {/* Delivery Cost */}
        <div className="flex justify-between items-center">
          <span className="font-sans font-normal text-body-2 text-text-grey-dark">
            Доставка
          </span>
          <span className="font-sans font-normal text-body-2 text-text-black">
            {formatPrice(deliveryCost)}
          </span>
        </div>

        {/* Promo Code with Toggle */}
        {promoDiscount > 0 && (
          <CvetyToggle
            checked={usePromo}
            onCheckedChange={onPromoToggle}
            label={`Промокод: ${promoDiscount} бонусов`}
          />
        )}

        {/* Divider */}
        <div className="border-t border-bg-light pt-2">
          {/* Total */}
          <div className="flex justify-between items-center">
            <span className="font-sans font-semibold text-body-1 text-text-black">
              Итого
            </span>
            <span className="font-sans font-bold text-h4 text-text-black">
              {formatPrice(total)}
            </span>
          </div>
        </div>
        {/* Bonus System Link */}
        {promoDiscount > 0 && (
          <CvetyButton variant="link" size="sm" className="text-body-2">
            Как бонусная система работает
          </CvetyButton>
        )}
      </CvetyCardContent>
    </CvetyCard>
  );
}
