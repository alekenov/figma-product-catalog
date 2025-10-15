import svgPaths from "../imports/svg-rauipwsa5m";

function CvetyLogo() {
  return (
    <div className="h-[40px] relative shrink-0 w-[108px]">
      <div className="absolute contents left-0 right-0 top-0">
        {/* Main logo elements */}
        <div className="absolute h-[25.603px] left-[74.58%] right-[18.91%] top-[2.16px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 8 26">
            <path d={svgPaths.p1f414b80} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[12.676px] left-[76.44%] right-[12.35%] top-[14.97px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 13">
            <path d={svgPaths.p11cf8080} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[12.578px] left-[88.16%] right-0 top-[14.99px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 13">
            <path d={svgPaths.p32a0f680} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[28.558px] left-0 right-[75.16%] top-0">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 27 29">
            <path d={svgPaths.p2e975080} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[13.218px] left-[22.47%] right-[65.96%] top-[14.82px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 14">
            <path d={svgPaths.pc0c9d80} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[12.958px] left-[33.75%] right-[54.9%] top-[15.12px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 13 13">
            <path d={svgPaths.p7cdf180} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[18.361px] left-[48.55%] right-[46.77%] top-[9.73px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 6 19">
            <path d={svgPaths.p2f90be80} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[1.345px] left-[46.09%] right-[44.23%] top-[15.07px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 11 2">
            <path d={svgPaths.p2c72b580} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[24.852px] left-[50.6%] right-[31.36%] top-[15.15px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 25">
            <path d={svgPaths.p1547e80} fill="var(--brand-primary)" />
          </svg>
        </div>
        <div className="absolute h-[2.745px] left-[69.85%] right-[27.03%] top-[25.34px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 4 3">
            <path d={svgPaths.p377afa00} fill="var(--brand-primary)" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function ContactIcon() {
  return (
    <div className="relative shrink-0 size-[32px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
        <path d={svgPaths.p2bf38740} stroke="var(--text-primary)" />
      </svg>
    </div>
  );
}

function AuthIcon() {
  return (
    <div className="relative shrink-0 size-[32px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
        <path d={svgPaths.pc780080} stroke="var(--text-primary)" />
      </svg>
    </div>
  );
}

function BasketIcon({ itemCount = 0 }: { itemCount?: number }) {
  return (
    <div className="relative shrink-0 size-[32px]">
      <div className="absolute inset-0 overflow-clip">
        <div className="absolute inset-[9.38%_9.38%_8.1%_6.25%]">
          <div className="absolute inset-[9.38%_9.38%_15.63%_15.63%]">
            <div className="absolute inset-[-2.08%]">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 26 26">
                <path d={svgPaths.p37f18f00} stroke="var(--text-primary)" />
              </svg>
            </div>
          </div>
          {/* Badge - only show if itemCount > 0 */}
          {itemCount > 0 && (
            <div className="absolute bg-[var(--brand-primary)] inset-[46.88%_48.73%_8.1%_6.25%] rounded-[27px]">
              <div className="flex flex-row items-center justify-center relative size-full">
                <div className="box-border content-stretch flex gap-[3px] items-center justify-center px-[10px] py-[5px] relative size-full">
                  <p className="text-[10px] text-nowrap text-white whitespace-pre font-normal">
                    {itemCount}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MenuIcon() {
  return (
    <div className="relative shrink-0 size-[28px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 28 28">
        <path d="M2 2.5H26M2 14H26M2 25.5H26" stroke="var(--text-primary)" />
      </svg>
    </div>
  );
}

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

interface HeaderProps {
  onNavigate?: (page: PageType, data?: { storeId?: string; productId?: string }) => void;
  itemCount?: number;
}

export function Header({ onNavigate, itemCount = 0 }: HeaderProps) {
  return (
    <header className="flex items-center justify-between w-full pt-[var(--spacing-4)]">
      <button onClick={() => onNavigate?.('home')} aria-label="На главную">
        <CvetyLogo />
      </button>
      <div className="flex items-center gap-[var(--spacing-4)]">
        <div className="flex items-center gap-[var(--spacing-3)]">
          <button onClick={() => onNavigate?.('home')} aria-label="Контакты">
            <ContactIcon />
          </button>
          <button onClick={() => onNavigate?.('profile')} aria-label="Профиль">
            <AuthIcon />
          </button>
        </div>
        <button onClick={() => onNavigate?.('cart')} aria-label="Корзина">
          <BasketIcon itemCount={itemCount} />
        </button>
        <button aria-label="Меню">
          <MenuIcon />
        </button>
      </div>
    </header>
  );
}