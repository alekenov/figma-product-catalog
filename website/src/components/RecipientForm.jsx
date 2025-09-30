import React from 'react';
import CvetyInput from './ui/cvety-input';
import CvetyCheckbox from './ui/CvetyCheckbox';

/**
 * RecipientForm - форма получателя заказа
 *
 * @param {string} recipientName - Имя получателя
 * @param {string} recipientPhone - Телефон получателя
 * @param {string} deliveryAddress - Адрес доставки
 * @param {boolean} isSelfRecipient - Получатель будет я
 * @param {function} onRecipientNameChange - Колбэк изменения имени
 * @param {function} onRecipientPhoneChange - Колбэк изменения телефона
 * @param {function} onDeliveryAddressChange - Колбэк изменения адреса
 * @param {function} onSelfRecipientToggle - Колбэк переключения "Получатель будет я"
 */
export default function RecipientForm({
  recipientName,
  recipientPhone,
  deliveryAddress,
  isSelfRecipient = false,
  onRecipientNameChange,
  onRecipientPhoneChange,
  onDeliveryAddressChange,
  onSelfRecipientToggle
}) {
  return (
    <div className="space-y-3">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-body-1 text-text-black">
        Оформление заказа
      </h3>

      {/* Subsection Title */}
      <label className="font-sans font-normal text-field-title text-text-grey-dark">
        Получатель
      </label>

      {/* Checkbox "Получателем буду я" */}
      <CvetyCheckbox
        checked={isSelfRecipient}
        onChange={onSelfRecipientToggle}
        label="Получателем буду я"
        size="sm"
      />

      {/* Recipient Name */}
      <CvetyInput
        value={recipientName}
        onChange={(e) => onRecipientNameChange(e.target.value)}
        placeholder="Имя получателя"
      />

      {/* Recipient Phone */}
      <CvetyInput
        type="tel"
        label="Телефон"
        value={recipientPhone}
        onChange={(e) => onRecipientPhoneChange(e.target.value)}
        placeholder="+7 (XXX) XXX XX XX"
      />

      {/* Delivery Address */}
      <CvetyInput
        label="Адрес доставки"
        value={deliveryAddress}
        onChange={(e) => onDeliveryAddressChange(e.target.value)}
        placeholder="Укажите адрес доставки"
      />
    </div>
  );
}