import React from 'react';
import { Link } from 'react-router-dom';
import svgPaths from '../../imports/svg-rauipwsa5m.ts';

function CvetyLogo() {
  return (
    <div className="h-10 w-[108px] text-pink">
      <div className="relative h-full w-full">
        <div className="absolute inset-0">
          <div className="absolute left-[74.58%] right-[18.91%] top-[2.16px] h-[25.603px]">
            <svg className="block h-full w-full" viewBox="0 0 8 26" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p1f414b80} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[76.44%] right-[12.35%] top-[14.97px] h-[12.676px]">
            <svg className="block h-full w-full" viewBox="0 0 13 13" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p11cf8080} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[88.16%] right-0 top-[14.99px] h-[12.578px]">
            <svg className="block h-full w-full" viewBox="0 0 13 13" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p32a0f680} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-0 right-[75.16%] top-0 h-[28.558px]">
            <svg className="block h-full w-full" viewBox="0 0 27 29" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p2e975080} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[22.47%] right-[65.96%] top-[14.82px] h-[13.218px]">
            <svg className="block h-full w-full" viewBox="0 0 13 14" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.pc0c9d80} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[33.75%] right-[54.9%] top-[15.12px] h-[12.958px]">
            <svg className="block h-full w-full" viewBox="0 0 13 13" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p7cdf180} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[48.55%] right-[46.77%] top-[9.73px] h-[18.361px]">
            <svg className="block h-full w-full" viewBox="0 0 6 19" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p2f90be80} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[46.09%] right-[44.23%] top-[15.07px] h-[1.345px]">
            <svg className="block h-full w-full" viewBox="0 0 11 2" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p2c72b580} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[50.6%] right-[31.36%] top-[15.15px] h-[24.852px]">
            <svg className="block h-full w-full" viewBox="0 0 20 25" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p1547e80} fill="currentColor" />
            </svg>
          </div>
          <div className="absolute left-[69.85%] right-[27.03%] top-[25.34px] h-[2.745px]">
            <svg className="block h-full w-full" viewBox="0 0 4 3" fill="none" preserveAspectRatio="none">
              <path d={svgPaths.p377afa00} fill="currentColor" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function ContactIcon() {
  return (
    <svg className="block h-8 w-8" viewBox="0 0 32 32" fill="none" preserveAspectRatio="none" aria-hidden="true">
      <path d={svgPaths.p2bf38740} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function AuthIcon() {
  return (
    <svg className="block h-8 w-8" viewBox="0 0 32 32" fill="none" preserveAspectRatio="none" aria-hidden="true">
      <path d={svgPaths.pc780080} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function BasketIcon() {
  return (
    <svg className="block h-8 w-8" viewBox="0 0 26 26" fill="none" preserveAspectRatio="none" aria-hidden="true">
      <path d={svgPaths.p37f18f00} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg className="block h-7 w-7" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <path d="M2 2.5H26M2 14H26M2 25.5H26" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function HeaderIconButton({ label, onClick, to, children, badge }) {
  const content = (
    <span className="relative inline-flex size-10 items-center justify-center rounded-full border border-bg-light bg-white text-text-black transition-colors hover:border-pink">
      {children}
      {badge}
      <span className="sr-only">{label}</span>
    </span>
  );

  if (to) {
    return (
      <Link to={to} aria-label={label} className="inline-flex">
        {content}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onClick} aria-label={label} className="inline-flex">
      {content}
    </button>
  );
}

function CartButton({ count = 0, onClick, to }) {
  const badge =
    count > 0 ? (
      <span className="absolute -right-1 -top-1 inline-flex min-w-[20px] items-center justify-center rounded-full bg-pink px-1 text-[11px] font-semibold leading-5 text-white">
        {count > 99 ? '99+' : count}
      </span>
    ) : null;

  return (
    <HeaderIconButton label="Открыть корзину" onClick={onClick} to={to} badge={badge}>
      <BasketIcon />
    </HeaderIconButton>
  );
}

export default function Header({
  cartCount = 0,
  onContactClick,
  onAuthClick,
  onCartClick,
  onMenuClick,
}) {
  return (
    <header className="w-full border-b border-bg-light bg-white px-4 pt-4">
      <div className="flex items-center justify-between gap-4">
        <Link to="/" aria-label="Cvety.kz — на главную" className="inline-flex">
          <CvetyLogo />
        </Link>

        <div className="flex items-center gap-3">
          <HeaderIconButton label="Контакты" onClick={onContactClick}>
            <ContactIcon />
          </HeaderIconButton>
          <HeaderIconButton label="Войти" onClick={onAuthClick}>
            <AuthIcon />
          </HeaderIconButton>
          <CartButton count={cartCount} onClick={onCartClick} to="/cart" />
          <HeaderIconButton label="Открыть меню" onClick={onMenuClick}>
            <MenuIcon />
          </HeaderIconButton>
        </div>
      </div>
    </header>
  );
}
