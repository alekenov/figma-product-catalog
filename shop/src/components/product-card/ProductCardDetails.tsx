import svgPaths from "../../imports/svg-r3kfi35k7m";

// Delivery and timing section
function DeliveryOptions() {
  const deliveryOptions = [
    {
      id: 'express',
      title: 'Экспресс доставка',
      subtitle: 'Доставим через 30 минут',
      price: '+ 500 ₸',
      selected: true,
    },
    {
      id: 'standard',
      title: 'Стандартная доставка',
      subtitle: 'Доставим сегодня к 18:00',
      price: 'Бесплатно',
      selected: false,
    },
    {
      id: 'pickup',
      title: 'Самовывоз',
      subtitle: 'Готов через 15 минут',
      price: 'Бесплатно',
      selected: false,
    },
  ];

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-4">Способ получения</h3>
      
      <div className="space-y-3">
        {deliveryOptions.map((option) => (
          <button
            key={option.id}
            className={`relative w-full p-4 rounded-2xl border transition-all text-left ${
              option.selected 
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium text-[var(--text-primary)] mb-1">
                  {option.title}
                </p>
                <p className="text-sm text-[var(--text-secondary)]">
                  {option.subtitle}
                </p>
              </div>
              <div className="ml-3 text-right">
                <p className={`text-sm font-medium ${
                  option.price === 'Бесплатно' 
                    ? 'text-[var(--brand-success)]' 
                    : 'text-[var(--text-primary)]'
                }`}>
                  {option.price}
                </p>
              </div>
            </div>
            
            {option.selected && (
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
        ))}
      </div>
    </div>
  );
}

// Additional services section
function AdditionalServices() {
  const services = [
    {
      id: 'card',
      title: 'Открытка с пожеланиями',
      description: 'Красивая открытка с вашим текстом',
      price: '+ 200 ₸',
      selected: false,
    },
    {
      id: 'wrapping',
      title: 'Праздничная упаковка',
      description: 'Дополнительная подарочная упаковка',
      price: '+ 300 ₸',
      selected: true,
    },
    {
      id: 'ribbon',
      title: 'Атласная лента',
      description: 'Красивая лента для украшения',
      price: '+ 150 ₸',
      selected: false,
    },
    {
      id: 'chocolates',
      title: 'Шоколадные конфеты',
      description: 'Коробка премиальных конфет',
      price: '+ 1 500 ₸',
      selected: false,
    },
  ];

  return (
    <div className="mt-[var(--spacing-4)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-4">Дополнительно</h3>
      
      <div className="space-y-3">
        {services.map((service) => (
          <button
            key={service.id}
            className={`relative w-full p-4 rounded-2xl border transition-all text-left ${
              service.selected 
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium text-[var(--text-primary)] mb-1">
                  {service.title}
                </p>
                <p className="text-sm text-[var(--text-secondary)]">
                  {service.description}
                </p>
              </div>
              <div className="ml-3 text-right">
                <p className="text-sm font-medium text-[var(--text-primary)]">
                  {service.price}
                </p>
              </div>
            </div>
            
            {service.selected && (
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
        ))}
      </div>
    </div>
  );
}

// Recipient information section
function RecipientInfo() {
  return (
    <div className="mt-[var(--spacing-4)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-4">Информация о получателе</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
            Имя получателя
          </label>
          <input
            type="text"
            placeholder="Введите имя получателя"
            className="w-full p-3 bg-[var(--background-secondary)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-colors"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
            Телефон получателя
          </label>
          <input
            type="tel"
            placeholder="+7 (___) ___-__-__"
            className="w-full p-3 bg-[var(--background-secondary)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-colors"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
            Адрес доставки
          </label>
          <textarea
            placeholder="Введите точный адрес доставки"
            rows={3}
            className="w-full p-3 bg-[var(--background-secondary)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-colors resize-none"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
            Комментарий к заказу (необязательно)
          </label>
          <textarea
            placeholder="Особые пожелания или инструкции"
            rows={2}
            className="w-full p-3 bg-[var(--background-secondary)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent transition-colors resize-none"
          />
        </div>
      </div>
    </div>
  );
}

// Time selection section
function TimeSelection() {
  const timeSlots = [
    { id: 'now', label: 'Как можно скорее', selected: true },
    { id: 'time1', label: '14:00 - 15:00', selected: false },
    { id: 'time2', label: '15:00 - 16:00', selected: false },
    { id: 'time3', label: '16:00 - 17:00', selected: false },
    { id: 'time4', label: '17:00 - 18:00', selected: false },
    { id: 'custom', label: 'Другое время', selected: false },
  ];

  return (
    <div className="mt-[var(--spacing-4)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-4">Время доставки</h3>
      
      <div className="grid grid-cols-2 gap-2">
        {timeSlots.map((slot) => (
          <button
            key={slot.id}
            className={`relative p-3 rounded-2xl border transition-all text-center text-sm ${
              slot.selected 
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            {slot.label}
            
            {slot.selected && (
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
        ))}
      </div>
    </div>
  );
}

// Main details component
export function ProductCardDetails() {
  return (
    <div className="p-[var(--spacing-4)] bg-[var(--background-secondary)] space-y-[var(--spacing-4)]">
      <DeliveryOptions />
      <TimeSelection />
      <AdditionalServices />
      <RecipientInfo />
    </div>
  );
}