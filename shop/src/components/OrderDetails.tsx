import { CvetyInput } from './ui/cvety-input';
import { CvetyTextarea } from './ui/cvety-textarea';
import { CvetyButton } from './ui/cvety-button';
import { useState } from 'react';

interface OrderDetailsProps {
  isEditable?: boolean;
}

export function OrderDetails({ isEditable = true }: OrderDetailsProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Состояние для редактируемых полей
  const [editData, setEditData] = useState({
    recipient: 'Ксения',
    phone: '+7 (917) 096-5427',
    address: 'г. Астана, ул. Сарайшык, 127',
    deliveryDate: '2024-01-30',
    deliveryTime: '14:24',
    comment: 'Поздравление с днем рождения!',
    cardText: 'Дорогая Ксения! Поздравляю тебя с днем рождения! Желаю счастья, здоровья и много радостных моментов! 🌹'
  });

  const [originalData] = useState(editData);

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsSaving(false);
    setIsEditing(false);
    console.log('Order updated:', editData);
  };

  const handleCancel = () => {
    setEditData(originalData);
    setIsEditing(false);
  };

  const orderInfo = [
    { 
      key: 'recipient',
      label: 'Получатель', 
      value: `${editData.recipient}, ${editData.phone}`,
      editable: true
    },
    { 
      key: 'address',
      label: 'Адрес доставки', 
      value: editData.address,
      editable: true
    },
    { 
      key: 'datetime',
      label: 'Дата и время', 
      value: `${new Date(editData.deliveryDate).toLocaleDateString('ru-RU', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })}, ${editData.deliveryTime}`,
      editable: true
    },
    { 
      key: 'comment',
      label: 'Комментарий к заказу', 
      value: editData.comment,
      editable: true
    },
    { 
      key: 'cardText',
      label: 'Текст открытки', 
      value: editData.cardText,
      editable: true
    }
  ];

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <div className="flex items-center justify-between">
        <h2 className="text-[var(--text-primary)] font-medium">Детали заказа</h2>
        
        {isEditable && !isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 text-[var(--brand-primary)] border border-[var(--brand-primary)] rounded-[var(--radius-md)] text-sm font-medium hover:bg-[var(--brand-primary)]/5 transition-colors"
          >
            Редактировать
          </button>
        )}
      </div>

      {!isEditable && (
        <div className="p-[var(--spacing-3)] bg-[var(--background-secondary)] rounded-[var(--radius-md)]">
          <p className="text-[var(--text-secondary)] text-sm">
            ⚠️ Заказ нельзя изменить, так как он уже передан курьеру
          </p>
        </div>
      )}
      
      <div className="space-y-[var(--spacing-4)]">
        {!isEditing ? (
          <div className="space-y-[var(--spacing-3)]">
            {orderInfo.map((info, index) => (
              <div key={index} className="space-y-[var(--spacing-1)]">
                <p className="text-[var(--text-secondary)] text-sm">{info.label}</p>
                <p className="text-[var(--text-primary)]">{info.value}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-[var(--spacing-4)]">
            <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
              <CvetyInput
                label="Имя получателя"
                value={editData.recipient}
                onChange={(e) => setEditData({...editData, recipient: e.target.value})}
              />
              <CvetyInput
                label="Телефон"
                value={editData.phone}
                onChange={(e) => setEditData({...editData, phone: e.target.value})}
              />
            </div>
            
            <CvetyInput
              label="Адрес доставки"
              value={editData.address}
              onChange={(e) => setEditData({...editData, address: e.target.value})}
            />
            
            <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
              <CvetyInput
                label="Дата доставки"
                type="date"
                value={editData.deliveryDate}
                onChange={(e) => setEditData({...editData, deliveryDate: e.target.value})}
              />
              <CvetyInput
                label="Время доставки"
                type="time"
                value={editData.deliveryTime}
                onChange={(e) => setEditData({...editData, deliveryTime: e.target.value})}
              />
            </div>
            
            <CvetyInput
              label="Комментарий к заказу"
              value={editData.comment}
              onChange={(e) => setEditData({...editData, comment: e.target.value})}
            />
            
            <CvetyTextarea
              label="Текст открытки"
              value={editData.cardText}
              onChange={(e) => setEditData({...editData, cardText: e.target.value})}
              className="min-h-[80px]"
            />
            
            <div className="flex gap-[var(--spacing-3)]">
              <CvetyButton 
                variant="primary" 
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1"
              >
                {isSaving ? 'Сохранение...' : 'Сохранить'}
              </CvetyButton>
              <CvetyButton 
                variant="secondary" 
                onClick={handleCancel}
                disabled={isSaving}
                className="flex-1"
              >
                Отменить
              </CvetyButton>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}