import { Clock } from 'lucide-react';
import { useOrderForm } from '../contexts/OrderFormContext';

interface TimeSlot {
  id: string;
  label: string;
  available: boolean;
}

interface DateOption {
  id: string;
  label: string;
  timeSlots: TimeSlot[];
}

const deliveryOptions: DateOption[] = [
  {
    id: 'today',
    label: 'Сегодня',
    timeSlots: [
      { id: 'express', label: '120-150 мин', available: true },
      { id: 'slot1', label: '18:00-19:00', available: true },
      { id: 'slot2', label: '19:00-20:00', available: true },
      { id: 'slot3', label: '20:00-21:00', available: true }
    ]
  },
  {
    id: 'tomorrow',
    label: 'Завтра',
    timeSlots: [
      { id: 'express-tom', label: '120-150 мин', available: true },
      { id: 'slot1-tom', label: '09:00-10:00', available: true },
      { id: 'slot2-tom', label: '10:00-11:00', available: true },
      { id: 'slot3-tom', label: '11:00-12:00', available: true },
      { id: 'slot4-tom', label: '12:00-13:00', available: true },
      { id: 'slot5-tom', label: '13:00-14:00', available: true }
    ]
  }
];

function DateTab({ 
  option, 
  isSelected, 
  onSelect 
}: { 
  option: DateOption; 
  isSelected: boolean; 
  onSelect: () => void; 
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`relative flex items-center gap-2 px-4 py-2 rounded-2xl transition-all border ${
        isSelected 
          ? 'bg-white text-[var(--text-primary)] border-[var(--border)]' 
          : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
      }`}
    >
      <Clock size={14} />
      <span className="text-label">{option.label}</span>
      {isSelected && (
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path 
              d="M2 5L4 7L8 3" 
              stroke="white" 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}
    </button>
  );
}

function TimeSlotPill({ 
  slot, 
  isSelected, 
  onSelect 
}: { 
  slot: TimeSlot; 
  isSelected: boolean; 
  onSelect: () => void; 
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`relative px-3 py-2 rounded-2xl transition-all text-label whitespace-nowrap border flex-shrink-0 ${
        isSelected 
          ? 'bg-white text-[var(--text-primary)] border-[var(--border)]' 
          : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
      }`}
    >
      {slot.label}
      {isSelected && (
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path 
              d="M2 5L4 7L8 3" 
              stroke="white" 
              strokeWidth="1.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}
    </button>
  );
}

export function DeliveryTimeSelector() {
  const { deliveryTime, setDeliveryTime } = useOrderForm();

  const selectedDateOption = deliveryOptions.find(option => option.id === deliveryTime.selectedDate);

  const handleDateChange = (dateId: string) => {
    const dateOption = deliveryOptions.find(opt => opt.id === dateId);
    if (dateOption && dateOption.timeSlots.length > 0) {
      const firstSlot = dateOption.timeSlots[0];
      setDeliveryTime({
        selectedDate: dateId,
        selectedTimeSlot: firstSlot.id,
        selectedTimeLabel: firstSlot.label
      });
    }
  };

  const handleTimeSlotChange = (slotId: string, slotLabel: string) => {
    setDeliveryTime({
      ...deliveryTime,
      selectedTimeSlot: slotId,
      selectedTimeLabel: slotLabel
    });
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      <p className="text-subtitle text-[var(--text-primary)]">
        Дата и время
      </p>
      
      {/* Clock Icon + Date Tabs */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center flex-shrink-0">
          <Clock size={16} className="text-white" />
        </div>
        
        <div className="flex gap-1">
          {deliveryOptions.map((option) => (
            <DateTab
              key={option.id}
              option={option}
              isSelected={deliveryTime.selectedDate === option.id}
              onSelect={() => handleDateChange(option.id)}
            />
          ))}
        </div>
      </div>
      
      {/* Time Slots */}
      {selectedDateOption && selectedDateOption.timeSlots.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 pt-2">
          {selectedDateOption.timeSlots.map((slot) => (
            <TimeSlotPill
              key={slot.id}
              slot={slot}
              isSelected={deliveryTime.selectedTimeSlot === slot.id}
              onSelect={() => handleTimeSlotChange(slot.id, slot.label)}
            />
          ))}
        </div>
      )}
    </div>
  );
}