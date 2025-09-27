import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { clientsAPI } from './services/api';
import './App.css';

const AddClient = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    customerName: '',
    phone: '',
    notes: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Format phone number
  const formatPhoneNumber = (value) => {
    // Remove all non-digit characters
    const numbers = value.replace(/\D/g, '');

    // Limit to 11 digits (Kazakhstan format)
    const limited = numbers.slice(0, 11);

    if (limited.length === 0) return '';

    // Format as +7 XXX XXX XXXX
    let formatted = '';
    if (limited.length > 0) {
      // If starts with 7 or 8, replace with 7
      const normalized = limited[0] === '8' ? '7' + limited.slice(1) : limited;

      if (normalized.length <= 1) {
        formatted = '+' + normalized;
      } else if (normalized.length <= 4) {
        formatted = `+${normalized[0]} ${normalized.slice(1)}`;
      } else if (normalized.length <= 7) {
        formatted = `+${normalized[0]} ${normalized.slice(1, 4)} ${normalized.slice(4)}`;
      } else {
        formatted = `+${normalized[0]} ${normalized.slice(1, 4)} ${normalized.slice(4, 7)} ${normalized.slice(7)}`;
      }
    }

    return formatted;
  };

  // Handle phone input
  const handlePhoneChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setFormData({ ...formData, phone: formatted });
  };

  // Handle form submit
  const handleSubmit = async () => {
    // Validation
    if (!formData.customerName.trim()) {
      setSubmitError('Введите имя клиента');
      return;
    }

    if (!formData.phone || formData.phone.replace(/\s/g, '').length < 11) { // Check for 11 digits
      setSubmitError('Введите корректный номер телефона');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const clientData = {
        customerName: formData.customerName.trim(),
        phone: formData.phone.replace(/\s/g, ''), // Remove spaces for API
        notes: formData.notes.trim()
      };

      await clientsAPI.createClient(clientData);

      // Navigate back to clients list
      navigate('/clients');
    } catch (error) {
      console.error('Error creating client:', error);
      setSubmitError(error.message || 'Ошибка при создании клиента');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center px-4 mt-5 mb-6">
        <button
          onClick={() => navigate('/clients')}
          className="mr-4"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-[24px] font-['Open_Sans'] font-normal">Новый клиент</h1>
      </div>

      {/* Form */}
      <div className="px-4">
        {/* Customer Name */}
        <div className="mb-6">
          <label className="block text-[14px] font-['Open_Sans'] text-gray-disabled mb-2">
            Имя клиента *
          </label>
          <input
            type="text"
            value={formData.customerName}
            onChange={(e) => setFormData({ ...formData, customerName: e.target.value })}
            placeholder="Введите имя клиента"
            className="w-full px-4 py-3 bg-gray-input rounded-[12px] text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
          />
        </div>

        {/* Phone Number */}
        <div className="mb-6">
          <label className="block text-[14px] font-['Open_Sans'] text-gray-disabled mb-2">
            Номер телефона *
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={handlePhoneChange}
            placeholder="+7 777 123 4567"
            className="w-full px-4 py-3 bg-gray-input rounded-[12px] text-[16px] font-['Open_Sans'] placeholder-gray-placeholder"
            inputMode="numeric"
          />
        </div>

        {/* Notes */}
        <div className="mb-6">
          <label className="block text-[14px] font-['Open_Sans'] text-gray-disabled mb-2">
            Заметки
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Дополнительная информация о клиенте"
            rows={4}
            className="w-full px-4 py-3 bg-gray-input rounded-[12px] text-[16px] font-['Open_Sans'] placeholder-gray-placeholder resize-none"
          />
        </div>

        {/* Error Message */}
        {submitError && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 rounded-[12px]">
            <p className="text-[14px] font-['Open_Sans'] text-red-600">{submitError}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 mt-8 mb-6">
          <button
            onClick={() => navigate('/clients')}
            className="flex-1 py-3 bg-gray-input rounded-[12px] text-[16px] font-['Open_Sans'] font-semibold text-gray-disabled"
            disabled={isSubmitting}
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            className="flex-1 py-3 bg-purple-primary rounded-[12px] text-[16px] font-['Open_Sans'] font-semibold text-white disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddClient;