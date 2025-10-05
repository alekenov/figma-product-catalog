import { CvetyButton } from './ui/cvety-button';
import { useState } from 'react';

interface OrderActionsProps {
  onEditOrder?: () => void;
}

export function OrderActions({ onEditOrder }: OrderActionsProps) {
  const [orderStatus] = useState<'confirmed' | 'preparing' | 'delivering' | 'delivered'>('delivering');
  
  const canEdit = orderStatus === 'confirmed' || orderStatus === 'preparing';
  
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
      <CvetyButton variant="primary" fullWidth>
        Повторить заказ
      </CvetyButton>
      
      <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
        <CvetyButton variant="ghost" fullWidth>
          Поддержка
        </CvetyButton>
        <CvetyButton variant="ghost" fullWidth>
          Отменить заказ
        </CvetyButton>
      </div>
      
      {canEdit && (
        <CvetyButton variant="secondary" fullWidth onClick={onEditOrder}>
          Изменить заказ
        </CvetyButton>
      )}
    </div>
  );
}