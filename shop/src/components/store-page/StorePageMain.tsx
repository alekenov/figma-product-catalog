import svgPaths from "../../imports/svg-d37n8swoc1";
import { StorePageHeader } from './StorePageHeader';
import { StorePageProducts } from './StorePageProducts';
import { StorePageFooter } from './StorePageFooter';

// Header mobile component  
function HeaderMobileNew() {
  return (
    <div className="bg-white h-[var(--header-height)] flex items-center px-[var(--spacing-4)] border-b border-[var(--border)]">
      <button className="p-2 -ml-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
        <svg className="w-6 h-6 text-[var(--text-primary)]" fill="none" viewBox="0 0 24 24">
          <path d={svgPaths.p2bf77f00} fill="currentColor" />
        </svg>
      </button>
      
      <h1 className="flex-1 text-center text-title text-[var(--text-primary)]">
        Магазин
      </h1>
      
      <button className="p-2 -mr-2 rounded-full hover:bg-[var(--background-secondary)] transition-colors">
        <svg className="w-6 h-6 text-[var(--text-primary)]" fill="none" viewBox="0 0 24 24">
          <path d={svgPaths.p390b7c80} fill="currentColor" />
        </svg>
      </button>
    </div>
  );
}

// Store info components
function Component24IconTime() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / time">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / time">
          <path d={svgPaths.p26247900} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame9490() {
  return (
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 text-[var(--text-primary)]">
        <Component24IconTime />
      </div>
      <span className="text-body-emphasis text-[var(--text-primary)]">
        Режим работы:
      </span>
    </div>
  );
}

function Frame9516() {
  return (
    <div className="flex items-center gap-2">
      <span className="text-body-emphasis text-[var(--brand-error)]">
        Закрыто
      </span>
      <span className="text-body-emphasis text-[var(--text-primary)]">
        Откроется в 8:00
      </span>
    </div>
  );
}

function Component24IconArrowDown() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / arrow down">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / arrow down">
          <path d={svgPaths.p2b02a600} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame9447() {
  return (
    <button className="flex items-center gap-1 hover:bg-[var(--background-secondary)] rounded-md px-2 py-1 transition-colors">
      <Frame9516 />
      <div className="w-4 h-4 text-[var(--text-secondary)]">
        <Component24IconArrowDown />
      </div>
    </button>
  );
}

function Frame9492() {
  return (
    <div className="ml-9">
      <Frame9447 />
    </div>
  );
}

function Frame9491() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
      <Frame9490 />
      <Frame9492 />
    </div>
  );
}

// Delivery options components
function Component24IconDelivery() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / delivery">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / delivery">
          <g id="Vector">
            <path d={svgPaths.p37525400} fill="black" />
            <path d="M4 7H13V14H4V7Z" fill="var(--fill-0, white)" />
          </g>
        </g>
      </svg>
    </div>
  );
}

function Frame9517() {
  return (
    <span className="text-body-emphasis text-[var(--text-primary)]">
      Способ доставки:
    </span>
  );
}

function Frame9448() {
  return <Frame9517 />;
}

function Frame9510() {
  return (
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 text-[var(--text-primary)]">
        <Component24IconDelivery />
      </div>
      <Frame9448 />
    </div>
  );
}

// Delivery options picker
function Option() {
  return (
    <button className="flex-1 h-10 px-3 text-center text-caption text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
      <div className="space-y-0.5">
        <p className="text-body-emphasis">25 мин</p>
        <p>Курьером</p>
      </div>
    </button>
  );
}

function Option1() {
  return (
    <button className="flex-1 h-10 px-3 bg-white rounded-md shadow-sm border border-[var(--border)] text-center text-caption text-[var(--text-primary)] relative">
      <div className="space-y-0.5">
        <p className="text-body-emphasis">через 15 мин</p>
        <p>Самовывоз</p>
      </div>
      {/* Coral checkmark for selected option */}
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
    </button>
  );
}

function SegmentedPicker() {
  return (
    <div className="bg-[var(--background-secondary)] p-1 rounded-lg flex gap-1">
      <Option />
      <Option1 />
    </div>
  );
}

function Frame9782() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <Frame9510 />
      <SegmentedPicker />
    </div>
  );
}

// Main store content section
function Frame9786() {
  return (
    <div className="flex-1">
      <HeaderMobileNew />
      <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
        <StorePageHeader />
        <Frame9491 />
        <Frame9782 />
      </div>
    </div>
  );
}

// Main content section with products
function Frame9534() {
  return (
    <div className="bg-[var(--background-secondary)] px-[var(--spacing-4)] py-[var(--spacing-6)] space-y-[var(--spacing-6)]">
      <StorePageProducts />
    </div>
  );
}

// Main exported component
export default function StorePageRefactored() {
  return (
    <div className="bg-[var(--background-secondary)] min-h-screen">
      <div className="w-full max-w-sm mx-auto bg-white min-h-screen flex flex-col">
        <Frame9786 />
        <Frame9534 />
        <StorePageFooter />
      </div>
    </div>
  );
}