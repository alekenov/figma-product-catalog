import svgPaths from "../../imports/svg-d37n8swoc1";
import imgImage6 from "figma:asset/3503d8004f92c1b0ba0b038933311bcedb54ff09.png";
import imgImage7 from "figma:asset/a48251912860c71257feff0c580c1fba6e724118.png";
import imgImage8 from "figma:asset/a763c5f33269c2bbd4306454e16d47682fec708c.png";
import imgImage9 from "figma:asset/b748a97358f8796661d37dc271698d7380f38499.png";

// Photo pagination components
function PhotoPagination() {
  return (
    <div className="h-[2px] relative shrink-0 w-[22px]" data-name="Photo pagination">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 2">
        <g id=" Photo pagination">
          <path d={svgPaths.p3043a100} fill="var(--fill-0, #FF6666)" id="Rectangle 260" />
        </g>
      </svg>
    </div>
  );
}

function PhotoPagination1() {
  return (
    <div className="h-[2px] relative shrink-0 w-[22px]" data-name="Photo pagination">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 2">
        <g id=" Photo pagination">
          <path d={svgPaths.p3043a100} fill="var(--fill-0, white)" id="Rectangle 261" />
        </g>
      </svg>
    </div>
  );
}

function Component3() {
  return (
    <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex gap-1">
      <PhotoPagination />
      {[...Array(4).keys()].map((_, i) => (
        <PhotoPagination1 key={i} />
      ))}
    </div>
  );
}

// Plus button component
function Component24OutlinedSuggestedSymbolPlus1() {
  return (
    <div className="relative shrink-0 size-[20px]" data-name="24/ outlined / suggested / symbol / plus">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
        <g id="24/ outlined / suggested / symbol / plus">
          <path d={svgPaths.p13533d00} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function ButtonInCard1() {
  return (
    <button className="w-8 h-8 bg-[var(--background-secondary)] hover:bg-[var(--neutral-200)] rounded-full flex items-center justify-center transition-colors flex-shrink-0">
      <Component24OutlinedSuggestedSymbolPlus1 />
    </button>
  );
}

// Price components
function PriceInCard1() {
  return (
    <p className="text-price text-[var(--text-primary)]">
      7 900 ₸
    </p>
  );
}

function PriceInCard2() {
  return (
    <p className="text-price text-[var(--text-primary)]">
      7 900 ₸
    </p>
  );
}

// Product info components
function Frame1576() {
  return (
    <h4 className="text-body text-[var(--text-primary)] line-clamp-2">
      Розовые розы с оформлением
    </h4>
  );
}

function Frame1577() {
  return (
    <h4 className="text-body text-[var(--text-primary)] line-clamp-2">
      Розовые розы с оформлением
    </h4>
  );
}

function Component4() {
  return (
    <div className="space-y-1">
      <Frame1576 />
      <p className="text-micro text-[var(--text-secondary)]">
        Доставим сегодня к 15:30
      </p>
    </div>
  );
}

function Component8() {
  return (
    <div className="space-y-1">
      <Frame1577 />
      <p className="text-micro text-[var(--text-secondary)]">
        Доставим сегодня к 15:30
      </p>
    </div>
  );
}

// Text blocks with buttons
function Component5() {
  return (
    <div className="flex-1 space-y-2">
      <PriceInCard1 />
      <Component4 />
    </div>
  );
}

function Component9() {
  return (
    <div className="flex-1 space-y-2">
      <PriceInCard2 />
      <Component8 />
    </div>
  );
}

function Component6() {
  return (
    <div className="flex items-start justify-between gap-2">
      <Component5 />
      <ButtonInCard1 />
    </div>
  );
}

function Component10() {
  return (
    <div className="flex items-start justify-between gap-2">
      <Component9 />
      <ButtonInCard1 />
    </div>
  );
}

// Pagination for second product
function PhotoPagination5() {
  return (
    <div className="h-[2px] relative shrink-0 w-[22px]" data-name="Photo pagination">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 2">
        <g id=" Photo pagination">
          <path d={svgPaths.p3043a100} fill="var(--fill-0, #FF6666)" id="Rectangle 260" />
        </g>
      </svg>
    </div>
  );
}

function PhotoPagination6() {
  return (
    <div className="h-[2px] relative shrink-0 w-[22px]" data-name="Photo pagination">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 2">
        <g id=" Photo pagination">
          <path d={svgPaths.p3043a100} fill="var(--fill-0, white)" id="Rectangle 261" />
        </g>
      </svg>
    </div>
  );
}

function Component7() {
  return (
    <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex gap-1">
      <PhotoPagination5 />
      {[...Array(4).keys()].map((_, i) => (
        <PhotoPagination6 key={i} />
      ))}
    </div>
  );
}

// Product card components
function ProductCardInTheCatalog() {
  return (
    <div className="bg-white rounded-[var(--radius-md)] overflow-hidden hover:shadow-sm transition-shadow">
      <div className="relative aspect-square">
        <img 
          alt="Розовые розы с оформлением" 
          className="w-full h-full object-cover" 
          src={imgImage6} 
        />
        <Component3 />
      </div>
      <div className="p-[var(--spacing-3)]">
        <Component6 />
      </div>
    </div>
  );
}

function ProductCardInTheCatalog1() {
  return (
    <div className="bg-white rounded-[var(--radius-md)] overflow-hidden hover:shadow-sm transition-shadow">
      <div className="relative aspect-square">
        <img 
          alt="Розовые розы с оформлением" 
          className="w-full h-full object-cover" 
          src={imgImage7} 
        />
        <Component7 />
      </div>
      <div className="p-[var(--spacing-3)]">
        <Component10 />
      </div>
    </div>
  );
}

// Main products grid component
export function StorePageProducts() {
  return (
    <div className="space-y-[var(--spacing-4)]">
      <h3 className="text-title text-[var(--text-primary)]">Товары магазина</h3>
      <div className="grid grid-cols-2 gap-[var(--spacing-4)]">
        <ProductCardInTheCatalog />
        <ProductCardInTheCatalog1 />
      </div>
    </div>
  );
}