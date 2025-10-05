import React from 'react';
import CvetyInput from './ui/cvety-input';

/**
 * ContactDataForm - Контактные данные из Figma (352px width)
 *
 * @param {string} recipientName - Имя получателя
 * @param {function} onRecipientNameChange - Callback для имени
 * @param {string} recipientPhone - Телефон получателя
 * @param {function} onRecipientPhoneChange - Callback для телефона получателя
 * @param {string} senderPhone - Ваш телефон (отправителя)
 * @param {function} onSenderPhoneChange - Callback для телефона отправителя
 */
export default function ContactDataForm({
  recipientName = '',
  onRecipientNameChange,
  recipientPhone = '',
  onRecipientPhoneChange,
  senderPhone = '',
  onSenderPhoneChange
}) {
  return (
    <div style={{ width: '352px' }}>
      {/* Section Title */}
      <h3
        className="font-sans font-semibold text-[#000000] mb-4"
        style={{
          fontSize: '18px',
          lineHeight: '24.75px',
        }}
      >
        Контактные данные
      </h3>

      <div className="space-y-3">
        {/* Имя Input */}
        <CvetyInput
          label="Имя"
          value={recipientName}
          onChange={(e) => onRecipientNameChange(e.target.value)}
          placeholder="Имя получателя"
        />

        {/* Телефон получателя */}
        <CvetyInput
          label="Телефон"
          type="tel"
          value={recipientPhone}
          onChange={(e) => onRecipientPhoneChange(e.target.value)}
          placeholder="Телефон получателя"
        />

        {/* Ваш телефон (отправителя) */}
        <CvetyInput
          label="Ваш телефон"
          type="tel"
          value={senderPhone}
          onChange={(e) => onSenderPhoneChange(e.target.value)}
          placeholder="Номер заказчика"
        />
      </div>
    </div>
  );
}
