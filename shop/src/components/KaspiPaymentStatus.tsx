import { CvetyCard } from './ui/cvety-card';
import { CvetyButton } from './ui/cvety-button';

interface KaspiPaymentStatusProps {
  phone: string;
  status?: 'Wait' | 'Processed' | 'Error';
  externalId?: string;
}

export function KaspiPaymentStatus({ phone, status, externalId }: KaspiPaymentStatusProps) {
  // If no Kaspi payment data, don't render anything
  if (!status || !externalId) {
    return null;
  }

  const handleChangePhone = () => {
    // TODO: Implement phone number change functionality
    // This would require a backend endpoint to recreate the Kaspi payment
    alert('Функция изменения номера телефона в разработке');
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'Processed':
        return '✅';
      case 'Error':
        return '❌';
      case 'Wait':
      default:
        return '⏳';
    }
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'Processed':
        return 'Оплачено';
      case 'Error':
        return 'Ошибка оплаты';
      case 'Wait':
      default:
        return 'Ожидает оплаты';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'Processed':
        return 'text-green-600';
      case 'Error':
        return 'text-red-600';
      case 'Wait':
      default:
        return 'text-[var(--text-secondary)]';
    }
  };

  return (
    <CvetyCard variant="default" className="p-[var(--spacing-4)] space-y-[var(--spacing-3)]">
      {/* Status Header */}
      <div className="flex items-center gap-[var(--spacing-2)]">
        <span className="text-2xl">{getStatusIcon()}</span>
        <div>
          <h3 className="text-body-emphasis text-[var(--text-primary)]">
            Оплата Kaspi
          </h3>
          <p className={`text-caption ${getStatusColor()}`}>
            {getStatusMessage()}
          </p>
        </div>
      </div>

      {/* Payment Details */}
      {status === 'Wait' && (
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-body text-[var(--text-primary)]">
            Счет на оплату отправлен на ваш номер:
          </p>
          <p className="text-body-emphasis text-[var(--text-primary)]">
            {phone}
          </p>
          <p className="text-caption text-[var(--text-secondary)]">
            Откройте приложение Kaspi, проверьте раздел "Платежи" и оплатите заказ.
          </p>
        </div>
      )}

      {status === 'Processed' && (
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-body text-[var(--text-primary)]">
            Спасибо за оплату! Ваш заказ принят в работу.
          </p>
        </div>
      )}

      {status === 'Error' && (
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-body text-[var(--text-primary)]">
            Произошла ошибка при создании платежа. Пожалуйста, свяжитесь с нами.
          </p>
        </div>
      )}

      {/* Change Phone Button (only for Wait status) */}
      {status === 'Wait' && (
        <CvetyButton
          variant="outline"
          fullWidth
          size="sm"
          onClick={handleChangePhone}
        >
          Изменить номер телефона
        </CvetyButton>
      )}

      {/* Debug info (will be useful for development) */}
      {import.meta.env.DEV && externalId && (
        <div className="mt-[var(--spacing-2)] pt-[var(--spacing-2)] border-t border-[var(--border)]">
          <p className="text-caption text-[var(--text-tertiary)]">
            ID платежа: {externalId}
          </p>
        </div>
      )}
    </CvetyCard>
  );
}
