import { DeliveryMethodSelector, DeliveryMethod } from './DeliveryMethodSelector';
import { DeliveryTimeSelector } from './DeliveryTimeSelector';

interface CartHeaderProps {
  deliveryMethod: DeliveryMethod;
  onDeliveryMethodChange: (method: DeliveryMethod) => void;
}

export function CartHeader({ 
  deliveryMethod, 
  onDeliveryMethodChange 
}: CartHeaderProps) {
  return (
    <div className="space-y-[var(--spacing-4)]">
      <DeliveryMethodSelector 
        selectedMethod={deliveryMethod}
        onMethodChange={onDeliveryMethodChange}
      />
      
      {deliveryMethod === 'delivery' && (
        <DeliveryTimeSelector />
      )}
    </div>
  );
}