import svgPaths from "../imports/svg-rauipwsa5m";

function BouquetIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute h-[23.321px] left-[3px] top-px w-[19.867px]">
        <div className="absolute inset-[-2.14%_-2.52%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 25">
            <path d={svgPaths.p351813f0} stroke="#FF6666" strokeLinecap="round" />
            <path d={svgPaths.p133ba540} stroke="#FF6666" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function BalloonIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute inset-[-3.3%_8.74%_8.47%_3.85%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 25 27">
          <path d={svgPaths.p3518200} stroke="black" strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
}

function FruitsIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute h-[23px] left-[3px] top-[2px] w-[20px]">
        <div className="absolute inset-[-2.39%_-2.5%_-2.18%_-2.5%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 25">
            <path d={svgPaths.p2064f100} stroke="black" />
            <path d="M14 7L14.3509 8" stroke="black" />
            <path d="M17 9L17.3509 10" stroke="black" />
            <path d="M15 11L15.3509 12" stroke="black" />
            <path d="M18 13L18.3509 14" stroke="black" />
            <path d="M16 15L16.3509 16" stroke="black" />
            <path d="M18 18L18.3509 19" stroke="black" />
            <path d="M16 20L16.3509 21" stroke="black" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function PlantsIcon() {
  return (
    <div className="relative shrink-0 size-[28px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 28">
        <path d={svgPaths.p32a25bc0} stroke="black" />
      </svg>
    </div>
  );
}

function ToysIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute h-[20px] left-px top-[3px] w-[24px]">
        <div className="absolute inset-[-2.5%_-2.08%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 26 22">
            <path d={svgPaths.p2ed4b340} stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p1f444200} stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p91f0600} stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p54afc80} stroke="black" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function CakeIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute h-[19.667px] left-[3px] top-[3px] w-[21px]">
        <div className="absolute inset-[-2.54%_-2.38%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 22">
            <path d={svgPaths.p125eaf00} stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p1a52ba80} stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p37efa480} stroke="black" strokeLinecap="round" />
            <path d="M7 6C7 5.05429 7 1.95029 7 1" stroke="black" strokeLinecap="round" />
            <path d={svgPaths.p102b28c0} stroke="black" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function GiftIcon() {
  return (
    <div className="relative shrink-0 size-[28px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 28">
        <path d={svgPaths.p1173aa00} stroke="black" />
      </svg>
    </div>
  );
}

function BasketIcon() {
  return (
    <div className="relative shrink-0 size-[28px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 28">
        <path d={svgPaths.p614140} stroke="black" />
      </svg>
    </div>
  );
}

function LingerieIcon() {
  return (
    <div className="overflow-clip relative shrink-0 size-[28px]">
      <div className="absolute h-[18px] left-[3px] top-[4px] w-[21px]">
        <div className="absolute inset-[-2.78%_-2.38%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 23 20">
            <path d={svgPaths.p1c4e5880} stroke="black" />
            <path d={svgPaths.p3cfffc00} stroke="black" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function CategoryItem({ icon, label, isActive = false }: { icon: React.ReactNode; label: string; isActive?: boolean }) {
  return (
    <button className="flex flex-col items-center gap-1 min-w-fit">
      {icon}
      <span className={`text-micro text-center whitespace-nowrap ${isActive ? 'text-[var(--brand-primary)]' : 'text-[var(--text-primary)]'}`}>
        {label}
      </span>
    </button>
  );
}

export function CategoryNavigation() {
  return (
    <div className="flex gap-6 overflow-x-auto pb-2 scrollbar-hide">
      <CategoryItem icon={<BouquetIcon />} label="Букеты" isActive />
      <CategoryItem icon={<BalloonIcon />} label="Шары" />
      <CategoryItem icon={<FruitsIcon />} label="Фрукты" />
      <CategoryItem icon={<PlantsIcon />} label="В горшке" />
      <CategoryItem icon={<ToysIcon />} label="Игрушки" />
      <CategoryItem icon={<CakeIcon />} label="Торты" />
      <CategoryItem icon={<GiftIcon />} label="Подарки" />
      <CategoryItem icon={<BasketIcon />} label="Корзины" />
      <CategoryItem icon={<LingerieIcon />} label="Белье" />
    </div>
  );
}