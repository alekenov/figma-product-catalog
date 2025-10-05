import { useState } from 'react';
import { CvetyInput } from './ui/cvety-input';

interface RecipientData {
  name: string;
  phone: string;
}

interface RecipientDataFormProps {
  value?: RecipientData;
  onChange?: (data: RecipientData) => void;
  hideTitle?: boolean;
}

export function RecipientDataForm({ value, onChange, hideTitle = false }: RecipientDataFormProps) {
  const [recipientData, setRecipientData] = useState<RecipientData>(
    value || { name: '', phone: '' }
  );

  const handleChange = (field: keyof RecipientData, fieldValue: string) => {
    const newData = { ...recipientData, [field]: fieldValue };
    setRecipientData(newData);
    onChange?.(newData);
  };

  return (
    <div className="flex flex-col gap-[var(--spacing-4)] w-full">
      {!hideTitle && (
        <p className="text-base text-[var(--text-primary)] font-normal leading-[1.1]">
          Данные получателя
        </p>
      )}
      
      <div className="space-y-[var(--spacing-3)]">
        <CvetyInput
          label="Имя"
          placeholder="Имя получателя"
          value={recipientData.name}
          onChange={(e) => handleChange('name', e.target.value)}
        />
        
        <CvetyInput
          label="Телефон"
          placeholder="Телефон получателя"
          type="tel"
          value={recipientData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
        />
      </div>
    </div>
  );
}