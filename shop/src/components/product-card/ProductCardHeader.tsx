import svgPaths from "../../imports/svg-r3kfi35k7m";

// Star rating SVG components
function Group() {
  return (
    <div className="absolute h-[25.603px] left-[74.58%] right-[18.91%] top-[2.16px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 26">
        <g>
          <path d={svgPaths.p1f414b80} fill="var(--brand-primary)" />
        </g>
      </svg>
    </div>
  );
}

function Group2() {
  return (
    <div className="absolute h-[12.676px] left-[76.44%] right-[12.35%] top-[14.97px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 13">
        <g>
          <path d={svgPaths.p11cf8080} fill="var(--brand-primary)" />
        </g>
      </svg>
    </div>
  );
}

function Group4() {
  return (
    <div className="absolute h-[12.578px] left-[88.16%] right-0 top-[14.99px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 13">
        <g>
          <path d={svgPaths.p32a0f680} fill="var(--brand-primary)" />
        </g>
      </svg>
    </div>
  );
}

function Group7() {
  return (
    <div className="absolute h-[28.558px] left-0 right-[75.16%] top-0">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 27 29">
        <g>
          <path d={svgPaths.p2e975080} fill="var(--brand-primary)" />
        </g>
      </svg>
    </div>
  );
}

function Group9() {
  return (
    <div className="absolute h-[13.218px] left-[22.47%] right-[65.96%] top-[14.82px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 14">
        <g>
          <path d={svgPaths.pc0c9d80} fill="var(--brand-primary)" />
        </g>
      </svg>
    </div>
  );
}

// Rating stars container
function Frame9563() {
  return (
    <div className="relative w-24 h-8">
      <Group />
      <Group2 />
      <Group4 />
      <Group7 />
      <Group9 />
    </div>
  );
}

// Header navigation icons
function Component24IconArrowLeft() {
  return (
    <div className="w-6 h-6">
      <svg className="block size-full" fill="none" viewBox="0 0 24 24">
        <path d={svgPaths.p3c0c000} fill="currentColor" />
      </svg>
    </div>
  );
}

function Component24IconSearch() {
  return (
    <div className="w-6 h-6">
      <svg className="block size-full" fill="none" viewBox="0 0 24 24">
        <path d={svgPaths.p26a7c00} fill="currentColor" />
      </svg>
    </div>
  );
}

function Component24IconHeart() {
  return (
    <div className="w-6 h-6">
      <svg className="block size-full" fill="none" viewBox="0 0 24 24">
        <path d={svgPaths.p37d1800} fill="currentColor" />
      </svg>
    </div>
  );
}

function Component24IconShoppingBasket() {
  return (
    <div className="w-6 h-6">
      <svg className="block size-full" fill="none" viewBox="0 0 24 24">
        <path d={svgPaths.p2df9a000} fill="currentColor" />
      </svg>
    </div>
  );
}

// Header navigation
function HeaderNavigation() {
  return (
    <div className="flex items-center justify-between p-[var(--spacing-4)]">
      {/* Back button */}
      <button className="p-2 -ml-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
        <Component24IconArrowLeft />
      </button>

      {/* Action buttons */}
      <div className="flex items-center gap-2">
        <button className="p-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
          <Component24IconSearch />
        </button>
        <button className="p-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
          <Component24IconHeart />
        </button>
        <button className="p-2 -mr-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
          <Component24IconShoppingBasket />
        </button>
      </div>
    </div>
  );
}

// Delivery address section
function DeliveryAddressSection() {
  return (
    <div className="px-[var(--spacing-4)] pb-[var(--spacing-4)]">
      <button className="flex items-center gap-2 p-3 bg-[var(--background-secondary)] rounded-[var(--radius-md)] w-full text-left hover:bg-[var(--neutral-200)] transition-colors">
        <div className="w-5 h-5 text-[var(--text-primary)]">
          <svg className="block size-full" fill="none" viewBox="0 0 19 19">
            <path d={svgPaths.p32543000} fill="currentColor" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-[var(--text-primary)] text-sm">
            Астана
          </p>
          <p className="text-xs text-[var(--text-secondary)] truncate">
            уточните адрес доставки...
          </p>
        </div>
      </button>
    </div>
  );
}

// Store info section
function StoreInfoSection() {
  return (
    <div className="px-[var(--spacing-4)] pb-[var(--spacing-4)]">
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] border border-[var(--border)]">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h2 className="font-semibold text-[var(--text-primary)] mb-1">
              Vetka - магазин цветов
            </h2>
            <div className="flex items-center gap-3 text-sm">
              <div className="flex items-center gap-1">
                <Frame9563 />
                <span className="font-medium text-[var(--text-primary)]">4.6</span>
              </div>
              <span className="text-[var(--text-secondary)]">164 отзыва</span>
              <span className="text-[var(--text-secondary)]">210 оценок</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            <button className="w-8 h-8 bg-[var(--brand-success)] rounded-full flex items-center justify-center hover:opacity-80 transition-opacity">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M8 1C4.13 1 1 4.13 1 8C1 9.29 1.35 10.5 1.97 11.54L1 15L4.46 14.03C5.5 14.65 6.71 15 8 15C11.87 15 15 11.87 15 8C15 4.13 11.87 1 8 1ZM11.5 11C11.36 11.31 10.96 11.59 10.61 11.67C10.33 11.74 9.98 11.8 8.97 11.4C7.71 10.9 6.31 9.5 5.81 8.24C5.56 7.61 5.56 7.11 5.8 6.7C5.94 6.44 6.19 6.31 6.36 6.31H6.81C6.94 6.31 7.09 6.3 7.17 6.56L7.67 7.81C7.74 7.97 7.7 8.17 7.56 8.31L7.31 8.56C7.31 8.56 7.31 8.81 7.81 9.56S8.69 10.19 8.69 10.19L8.94 9.94C9.08 9.8 9.28 9.76 9.44 9.83L10.69 10.33C10.95 10.41 10.94 10.56 10.94 10.69C10.94 10.81 10.81 11.06 10.55 11.2C10.53 11.21 10.51 11.21 10.5 11.21L11.5 11Z" 
                  fill="white"
                />
              </svg>
            </button>
            
            <button className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-500 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M8 1.5C5.8 1.5 4 3.3 4 5.5C4 6.1 4.1 6.6 4.3 7.1C4.2 7.1 4.1 7.1 4 7.1C2.3 7.1 1 8.4 1 10.1V12.5C1 13.3 1.7 14 2.5 14H13.5C14.3 14 15 13.3 15 12.5V10.1C15 8.4 13.7 7.1 12 7.1C11.9 7.1 11.8 7.1 11.7 7.1C11.9 6.6 12 6.1 12 5.5C12 3.3 10.2 1.5 8 1.5Z" 
                  fill="white"
                />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="text-xs text-[var(--text-secondary)]">
          Быстрая доставка • Свежие цветы • Гарантия качества
        </div>
      </div>
    </div>
  );
}

// Main header component
export function ProductCardHeader() {
  return (
    <div className="bg-white border-b border-[var(--border)]">
      <HeaderNavigation />
      <DeliveryAddressSection />
      <StoreInfoSection />
    </div>
  );
}