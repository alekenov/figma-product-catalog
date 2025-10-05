import { useState } from 'react';
import { CvetyInput } from './ui/cvety-input';

interface CustomerData {
  phone: string;
}

interface CustomerDataFormProps {
  value?: CustomerData;
  onChange?: (data: CustomerData) => void;
  hideTitle?: boolean;
}

export function CustomerDataForm({ value, onChange, hideTitle = false }: CustomerDataFormProps) {
  const [customerData, setCustomerData] = useState<CustomerData>(
    value || { phone: '' }
  );

  const handleChange = (field: keyof CustomerData, fieldValue: string) => {
    const newData = { ...customerData, [field]: fieldValue };
    setCustomerData(newData);
    onChange?.(newData);
  };

  return (
    <div className="flex flex-col gap-[var(--spacing-4)] w-full">
      {!hideTitle && (
        <p className="text-base text-[var(--text-primary)] font-normal leading-[1.1]">
          Данные заказчика
        </p>
      )}
      
      <div className="space-y-[var(--spacing-3)]">
        <CvetyInput
          label="Ваш телефон"
          placeholder="Номер заказчика"
          type="tel"
          value={customerData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
        />
      </div>
    </div>
  );
}