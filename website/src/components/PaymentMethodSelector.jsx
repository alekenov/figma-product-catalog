import React from 'react';
import { VisaIcon, MastercardIcon, BonusIcon, PayPalIcon, KaspiIcon } from '../assets/icons/SocialIcons';

/**
 * PaymentMethodSelector - выбор способа оплаты
 *
 * @param {string} selectedMethod - Выбранный способ оплаты ('visa', 'mastercard', 'bonus', 'paypal', 'kaspi')
 * @param {function} onMethodSelect - Колбэк при выборе способа оплаты
 */
export default function PaymentMethodSelector({ selectedMethod, onMethodSelect }) {
  const paymentMethods = [
    {
      id: 'cards',
      icons: [VisaIcon, MastercardIcon],
      label: 'Visa/Mastercard',
      width: 'w-[96px]'
    },
    {
      id: 'bonus',
      icons: [BonusIcon],
      label: 'Бонусы',
      width: 'w-[85px]'
    },
    {
      id: 'paypal',
      icons: [PayPalIcon],
      label: 'PayPal',
      width: 'w-[100px]'
    },
    {
      id: 'kaspi',
      icons: [KaspiIcon],
      label: 'Kaspi.kz',
      width: 'w-[105px]'
    }
  ];

  return (
    <div className="space-y-3">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-body-1 text-text-black">
        Способ оплаты
      </h3>

      {/* Payment Method Icons - Horizontal Scroll */}
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
        {paymentMethods.map(({ id, icons, label, width }) => (
          <button
            key={id}
            onClick={() => onMethodSelect(id)}
            className={`${width} h-[47px] flex items-center justify-center px-2 rounded-lg border-2 transition-colors shrink-0 ${
              selectedMethod === id
                ? 'border-pink bg-white'
                : 'border-bg-light bg-white hover:border-bg-extra-light'
            }`}
            aria-label={`Оплата через ${label}`}
          >
            <div className="flex items-center gap-1">
              {icons.map((Icon, index) => (
                <Icon key={index} className={icons.length > 1 ? "h-6" : "h-5"} />
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}