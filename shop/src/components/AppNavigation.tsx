import React, { useState } from 'react';
import { CvetyButton } from './ui/cvety-button';
import { CvetyCard, CvetyCardContent } from './ui/cvety-card';

// Import main app pages only
import { HomePage } from './HomePage';
import { ProductPageCard } from './ProductPageCard';
import { CartPage } from './CartPage';
import { OrderStatusPage } from './OrderStatusPage';
import { StorePage } from './StorePage';
import { StoresListPage } from './StoresListPage';
import { ProfilePage } from './ProfilePage';

type PageType = 'home' | 'product' | 'cart' | 'order-status' | 'store' | 'stores-list' | 'profile';

const pages = {
  'home': {
    title: 'Главная',
    component: HomePage,
    icon: '🏠'
  },
  'product': {
    title: 'Товар',
    component: ProductPageCard,
    icon: '🌹'
  },
  'cart': {
    title: 'Корзина',
    component: CartPage,
    icon: '🛒'
  },
  'order-status': {
    title: 'Статус заказа',
    component: OrderStatusPage,
    icon: '📦'
  },
  'store': {
    title: 'Магазин',
    component: StorePage,
    icon: '🏪'
  },
  'stores-list': {
    title: 'Все магазины',
    component: StoresListPage,
    icon: '🏬'
  },
  'profile': {
    title: 'Профиль',
    component: ProfilePage,
    icon: '👤'
  }
};

export function AppNavigation() {
  const [currentPage, setCurrentPage] = useState<PageType>('home');
  const [selectedStoreId, setSelectedStoreId] = useState<string>('vetka');
  const [selectedOrderId, setSelectedOrderId] = useState<string | undefined>();

  const handleStoreSelect = (storeId: string) => {
    setSelectedStoreId(storeId);
    setCurrentPage('store');
  };

  const handleNavigate = (page: PageType, data?: { storeId?: string; productId?: string; orderId?: string }) => {
    if (page === 'store' && data?.storeId) {
      handleStoreSelect(data.storeId);
    } else if (page === 'order-status' && data?.orderId) {
      setSelectedOrderId(data.orderId);
      setCurrentPage('order-status');
    } else {
      setCurrentPage(page);
    }
  };

  const renderCurrentPage = () => {
    if (currentPage === 'store') {
      return <StorePage storeId={selectedStoreId} onNavigate={handleNavigate} />;
    }
    if (currentPage === 'stores-list') {
      return <StoresListPage onStoreSelect={handleStoreSelect} />;
    }
    if (currentPage === 'home') {
      return <HomePage onNavigate={handleNavigate} />;
    }
    if (currentPage === 'cart') {
      return <CartPage onNavigate={handleNavigate} />;
    }
    if (currentPage === 'order-status') {
      return <OrderStatusPage orderId={selectedOrderId} />;
    }
    const PageComponent = pages[currentPage].component;
    return <PageComponent />;
  };

  return (
    <div className="bg-[var(--background-secondary)] min-h-screen w-full max-w-sm mx-auto relative">
      {/* Navigation Bar - Fixed at top */}
      <div className="fixed top-0 left-1/2 transform -translate-x-1/2 w-full max-w-sm bg-white border-b border-[var(--border)] z-50">
        <div className="p-[var(--spacing-3)] bg-white">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-medium text-[var(--text-primary)]">
              {pages[currentPage].icon} {pages[currentPage].title}
            </h2>
            <div className="text-xs text-[var(--text-secondary)]">
              Cvety.kz
            </div>
          </div>
          
          <div className="grid grid-cols-7 gap-1">
            {Object.entries(pages).map(([key, page]) => (
              <button
                key={key}
                onClick={() => setCurrentPage(key as PageType)}
                className={`relative text-xs py-2 px-2 h-auto flex flex-col gap-1 rounded-2xl transition-all border ${
                  currentPage === key 
                    ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                    : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
                }`}
              >
                <span className="text-sm">{page.icon}</span>
                <span className="text-[10px] leading-tight text-center">{page.title.split(' ')[0]}</span>
                {currentPage === key && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                    <svg width="8" height="8" viewBox="0 0 10 10" fill="none">
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
      </div>

      {/* Page Content - With top padding to account for fixed navigation */}
      <div className="pt-24">
        {renderCurrentPage()}
      </div>
    </div>
  );
}