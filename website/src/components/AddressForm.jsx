import React from 'react';
import CvetyCheckbox from './ui/CvetyCheckbox';
import CvetyInput from './ui/cvety-input';

/**
 * AddressForm - Форма адреса доставки из Figma (352px width)
 *
 * @param {boolean} askRecipient - "Узнать у получателя"
 * @param {function} onAskRecipientChange - Callback для checkbox
 * @param {string} deliveryAddress - Адрес доставки
 * @param {function} onDeliveryAddressChange - Callback для адреса
 * @param {string} floor - Этаж
 * @param {function} onFloorChange - Callback для этажа
 * @param {string} apartment - Кв/Офис
 * @param {function} onApartmentChange - Callback для кв/офиса
 * @param {string} notes - Примечания
 * @param {function} onNotesChange - Callback для примечаний
 */
export default function AddressForm({
  askRecipient = false,
  onAskRecipientChange,
  deliveryAddress = '',
  onDeliveryAddressChange,
  floor = '',
  onFloorChange,
  apartment = '',
  onApartmentChange,
  notes = '',
  onNotesChange
}) {
  return (
    <div style={{ width: '352px' }}>
      {/* Section Title */}
      <h3
        className="font-sans font-semibold text-[#000000] mb-4"
        style={{
          fontSize: '14px',
          lineHeight: '17.59375px',
        }}
      >
        Адрес доставки
      </h3>

      <div className="space-y-4">
        {/* Checkbox: Узнать у получателя */}
        <CvetyCheckbox
          checked={askRecipient}
          onChange={onAskRecipientChange}
          label="Узнать у получателя"
          size="sm"
        />

        {/* Адрес доставки Input */}
        <CvetyInput
          label="Адрес доставки"
          value={deliveryAddress}
          onChange={(e) => onDeliveryAddressChange(e.target.value)}
          placeholder="Введите адрес доставки"
        />

        {/* Row: Этаж + Кв/Офис (172px each with 8px gap) */}
        <div className="flex" style={{ gap: '8px' }}>
          <div style={{ width: '172px' }}>
            <CvetyInput
              label="Этаж"
              value={floor}
              onChange={(e) => onFloorChange(e.target.value)}
              placeholder="Этаж"
            />
          </div>
          <div style={{ width: '172px' }}>
            <CvetyInput
              label="Кв/Офис"
              value={apartment}
              onChange={(e) => onApartmentChange(e.target.value)}
              placeholder="№ кв/офиса"
            />
          </div>
        </div>

        {/* Примечания Textarea */}
        <CvetyInput
          as="textarea"
          label="Примечания"
          value={notes}
          onChange={(e) => onNotesChange(e.target.value)}
          placeholder="Домофон, особые указания"
          rows={3}
        />
      </div>
    </div>
  );
}
