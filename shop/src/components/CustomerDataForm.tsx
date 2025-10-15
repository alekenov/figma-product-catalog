import { useState, useEffect } from 'react';
import { CvetyInput } from './ui/cvety-input';
import { useOrderForm } from '../contexts/OrderFormContext';
import { validatePhone, formatPhoneInput } from '../utils/phoneValidation';

interface CustomerDataFormProps {
  hideTitle?: boolean;
}

export function CustomerDataForm({ hideTitle = false }: CustomerDataFormProps) {
  const { customer, setCustomer } = useOrderForm();
  const [phoneError, setPhoneError] = useState<string | undefined>();

  // Validate phone whenever it changes
  useEffect(() => {
    if (customer.phone) {
      const validation = validatePhone(customer.phone);
      setPhoneError(validation.isValid ? undefined : validation.errorMessage);
    } else {
      setPhoneError(undefined);
    }
  }, [customer.phone]);

  const handlePhoneChange = (value: string) => {
    // Filter input to allow only digits and +
    const formatted = formatPhoneInput(value);
    setCustomer({ ...customer, phone: formatted });
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
          placeholder="+7XXXXXXXXXX"
          type="tel"
          inputMode="tel"
          pattern="[+0-9]*"
          value={customer.phone}
          onChange={(e) => handlePhoneChange(e.target.value)}
          error={!!phoneError}
          helperText={phoneError}
        />
      </div>
    </div>
  );
}