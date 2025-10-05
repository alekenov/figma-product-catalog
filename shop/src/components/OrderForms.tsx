import { AddressSelector } from './AddressSelector';
import { RecipientDataForm } from './RecipientDataForm';
import { CustomerDataForm } from './CustomerDataForm';
import { DeliveryMethod } from './DeliveryMethodSelector';

interface OrderFormsProps {
  deliveryMethod: DeliveryMethod;
  onAddressSelect?: () => void;
}



export function OrderForms({ deliveryMethod, onAddressSelect }: OrderFormsProps) {
  return (
    <div className="space-y-[var(--spacing-6)]">
      <AddressSelector 
        deliveryMethod={deliveryMethod} 
        onAddressSelect={onAddressSelect} 
      />
      
      {/* Объединенная секция контактных данных */}
      <div className="flex flex-col gap-[var(--spacing-4)] w-full">
        <p className="text-subtitle text-[var(--text-primary)]">
          Контактные данные
        </p>
        
        <div className="space-y-[var(--spacing-3)]">
          {deliveryMethod === 'delivery' && <RecipientDataForm hideTitle />}
          <CustomerDataForm hideTitle />
        </div>
      </div>
    </div>
  );
}