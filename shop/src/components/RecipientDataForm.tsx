import { useState, useEffect } from 'react';
import { CvetyInput } from './ui/cvety-input';
import { useOrderForm } from '../contexts/OrderFormContext';
import { validatePhone, formatPhoneInput } from '../utils/phoneValidation';

interface RecipientDataFormProps {
  hideTitle?: boolean;
}

export function RecipientDataForm({ hideTitle = false }: RecipientDataFormProps) {
  const { recipient, setRecipient } = useOrderForm();
  const [phoneError, setPhoneError] = useState<string | undefined>();

  // Validate phone whenever it changes
  useEffect(() => {
    if (recipient.phone) {
      const validation = validatePhone(recipient.phone);
      setPhoneError(validation.isValid ? undefined : validation.errorMessage);
    } else {
      setPhoneError(undefined);
    }
  }, [recipient.phone]);

  const handleNameChange = (value: string) => {
    setRecipient({ ...recipient, name: value });
  };

  const handlePhoneChange = (value: string) => {
    // Filter input to allow only digits and +
    const formatted = formatPhoneInput(value);
    setRecipient({ ...recipient, phone: formatted });
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
          value={recipient.name}
          onChange={(e) => handleNameChange(e.target.value)}
        />

        <CvetyInput
          label="Телефон"
          placeholder="+7XXXXXXXXXX"
          type="tel"
          inputMode="tel"
          pattern="[+0-9]*"
          value={recipient.phone}
          onChange={(e) => handlePhoneChange(e.target.value)}
          error={!!phoneError}
          helperText={phoneError}
        />
      </div>
    </div>
  );
}