import React from 'react';
import CvetyButton from './ui/CvetyButton';

/**
 * CheckoutButton - трехсекционная кнопка оплаты
 *
 * @param {string} deliveryTime - Время доставки (например: "35 мин", "Завтра к 12:00")
 * @param {number} total - Итоговая сумма
 * @param {string} currency - Валюта (по умолчанию ₸)
 * @param {function} onClick - Колбэк при клике на кнопку
 * @param {boolean} disabled - Заблокирована ли кнопка
 */
export default function CheckoutButton({
  deliveryTime = '30 мин',
  total,
  currency = '₸',
  onClick,
  disabled = false
}) {
  const formatPrice = (price) => {
    return `${price.toLocaleString('ru-RU')} ${currency}`;
  };

  return (
    <CvetyButton
      variant="primary"
      size="lg"
      fullWidth
      onClick={onClick}
      disabled={disabled}
      className="!p-0"
    >
      <div className="flex items-center justify-between px-6 py-4 w-full">
        {/* Delivery Time */}
        <span className="flex-none">
          {deliveryTime}
        </span>

        {/* К оплате */}
        <span className="flex-1 text-center">
          К оплате
        </span>

        {/* Total */}
        <span className="flex-none font-bold">
          {formatPrice(total)}
        </span>
      </div>
    </CvetyButton>
  );
}