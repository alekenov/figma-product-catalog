import svgPaths from "../../imports/svg-r3kfi35k7m";

// Payment methods section
function PaymentMethods() {
  return (
    <div className="mb-[var(--spacing-4)]">
      <h4 className="font-medium text-[var(--text-primary)] mb-3">Способы оплаты</h4>
      <div className="flex items-center gap-2">
        {/* Visa */}
        <div className="w-12 h-8 bg-white rounded border border-[var(--border)] flex items-center justify-center">
          <svg width="24" height="8" viewBox="0 0 24 8" fill="none">
            <path d={svgPaths.p2dcc4600} fill="#005CA9" />
          </svg>
        </div>
        
        {/* MasterCard */}
        <div className="w-12 h-8 bg-white rounded border border-[var(--border)] flex items-center justify-center">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <div className="w-2 h-2 bg-orange-400 rounded-full -ml-1"></div>
          </div>
        </div>
        
        {/* PayPal */}
        <div className="w-12 h-8 bg-white rounded border border-[var(--border)] flex items-center justify-center">
          <span className="text-[8px] font-bold text-blue-600">PayPal</span>
        </div>
        
        {/* Apple Pay */}
        <div className="w-12 h-8 bg-white rounded border border-[var(--border)] flex items-center justify-center">
          <svg width="16" height="8" viewBox="0 0 16 8" fill="none">
            <path d="M3 1C2.5 1 2 1.5 2 2V6C2 6.5 2.5 7 3 7H13C13.5 7 14 6.5 14 6V2C14 1.5 13.5 1 13 1H3Z" fill="black"/>
          </svg>
        </div>
      </div>
    </div>
  );
}

// Order summary section
function OrderSummary() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] mb-[var(--spacing-4)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-4">Итого</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Букет "Розовые мечты"</span>
          <span className="text-[var(--text-primary)]">7 900 ₸</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Праздничная упаковка</span>
          <span className="text-[var(--text-primary)]">300 ₸</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Экспресс доставка</span>
          <span className="text-[var(--text-primary)]">500 ₸</span>
        </div>
        
        <div className="flex items-center justify-between text-[var(--brand-success)]">
          <span>Скидка постоянного клиента</span>
          <span>-400 ₸</span>
        </div>
        
        <div className="border-t border-[var(--border)] pt-3 mt-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-[var(--text-primary)]">К оплате</span>
            <span className="font-bold text-xl text-[var(--text-primary)]">8 300 ₸</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Action buttons section
function ActionButtons() {
  return (
    <div className="space-y-3 mb-[var(--spacing-6)]">
      <button className="w-full h-12 bg-[var(--brand-primary)] text-white font-medium rounded-[var(--radius-md)] hover:bg-[var(--brand-primary-dark)] transition-colors">
        Оформить заказ
      </button>
      
      <button className="w-full h-12 bg-white border border-[var(--border)] text-[var(--text-primary)] font-medium rounded-[var(--radius-md)] hover:bg-[var(--background-secondary)] transition-colors">
        Добавить в корзину
      </button>
    </div>
  );
}

// Guarantee section
function GuaranteeSection() {
  const guarantees = [
    {
      icon: (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path 
            d="M8 1L9.5 5.5H14L10.5 8.5L12 13L8 10L4 13L5.5 8.5L2 5.5H6.5L8 1Z" 
            fill="currentColor"
          />
        </svg>
      ),
      title: "Свежесть",
      description: "Только свежие цветы"
    },
    {
      icon: (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path 
            d="M8 1C4.5 1 2 3.5 2 7C2 10.5 8 15 8 15S14 10.5 14 7C14 3.5 11.5 1 8 1Z" 
            fill="currentColor"
          />
        </svg>
      ),
      title: "Доставка",
      description: "Точно в срок"
    },
    {
      icon: (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path 
            d="M8 1L9 4L12 4L9.5 6.5L10.5 9.5L8 7.5L5.5 9.5L6.5 6.5L4 4L7 4L8 1Z" 
            fill="currentColor"
          />
        </svg>
      ),
      title: "Качество",
      description: "100% гарантия"
    },
  ];

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] mb-[var(--spacing-4)]">
      <h4 className="font-medium text-[var(--text-primary)] mb-4">Наши гарантии</h4>
      
      <div className="grid grid-cols-3 gap-4">
        {guarantees.map((guarantee, index) => (
          <div key={index} className="text-center">
            <div className="w-10 h-10 bg-[var(--brand-primary)] rounded-full flex items-center justify-center text-white mx-auto mb-2">
              {guarantee.icon}
            </div>
            <p className="font-medium text-xs text-[var(--text-primary)] mb-1">
              {guarantee.title}
            </p>
            <p className="text-xs text-[var(--text-secondary)]">
              {guarantee.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Footer info section
function FooterInfo() {
  return (
    <div className="text-center">
      <div className="mb-4">
        <PaymentMethods />
      </div>
      
      <div className="space-y-2 text-xs text-[var(--text-secondary)]">
        <p>© 2024 Cvety.kz</p>
        <p>Доставка цветов по Астане и Алматы</p>
        <p>Режим работы: 08:00 - 22:00 без выходных</p>
        <p>
          <a href="tel:+77172999888" className="text-[var(--brand-primary)] hover:underline">
            +7 (717) 299-98-88
          </a>
        </p>
      </div>
      
      <div className="mt-4 pt-4 border-t border-[var(--border)]">
        <p className="text-xs text-[var(--text-secondary)]">
          Нажимая "Оформить заказ", вы соглашаетесь с{' '}
          <a href="#" className="text-[var(--brand-primary)] hover:underline">
            условиями доставки
          </a>{' '}
          и{' '}
          <a href="#" className="text-[var(--brand-primary)] hover:underline">
            политикой конфиденциальности
          </a>
        </p>
      </div>
    </div>
  );
}

// Main footer component
export function ProductCardFooter() {
  return (
    <div className="p-[var(--spacing-4)] bg-[var(--background-secondary)]">
      <OrderSummary />
      <GuaranteeSection />
      <ActionButtons />
      <FooterInfo />
    </div>
  );
}