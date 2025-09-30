import React from 'react';
import CvetyInput from './ui/cvety-input';

/**
 * SenderForm - форма отправителя заказа
 *
 * @param {string} senderPhone - Телефон отправителя
 * @param {function} onSenderPhoneChange - Колбэк изменения телефона
 */
export default function SenderForm({
  senderPhone,
  onSenderPhoneChange
}) {
  return (
    <div className="space-y-3">
      {/* Section Title */}
      <h3 className="font-sans font-semibold text-body-1 text-text-black">
        Отправитель
      </h3>

      {/* Sender Phone */}
      <CvetyInput
        type="tel"
        label="Ваш телефон"
        value={senderPhone}
        onChange={(e) => onSenderPhoneChange(e.target.value)}
        placeholder="+7 (XXX) XXX XX XX"
      />
    </div>
  );
}