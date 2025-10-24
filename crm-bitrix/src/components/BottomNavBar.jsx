import React from 'react';
import { Package2 } from 'lucide-react';

// Navigation icons as SVG components
const OrdersIcon = ({ isActive }) => (
  <svg className={`w-6 h-6 ${isActive ? 'stroke-purple-primary' : 'stroke-gray-disabled'}`} fill="none" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
    />
  </svg>
);

const ProductsIcon = ({ isActive }) => (
  <svg className={`w-6 h-6 ${isActive ? 'stroke-purple-primary' : 'stroke-gray-disabled'}`} fill="none" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M4 6h16l-1 10H5L4 6z M4 6l-1-2"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M7 10h2m4 0h2"
    />
  </svg>
);

const WarehouseIcon = ({ isActive }) => (
  <Package2
    className={`w-6 h-6 ${isActive ? 'stroke-purple-primary' : 'stroke-gray-disabled'}`}
    strokeWidth={2}
  />
);

const ClientsIcon = ({ isActive }) => (
  <svg className={`w-6 h-6 ${isActive ? 'stroke-purple-primary' : 'stroke-gray-disabled'}`} fill="none" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"
    />
    <circle
      cx="9"
      cy="7"
      r="4"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"
    />
  </svg>
);

const ProfileIcon = ({ isActive }) => (
  <svg className={`w-6 h-6 ${isActive ? 'stroke-purple-primary' : 'stroke-gray-disabled'}`} fill="none" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"
    />
    <circle
      cx="12"
      cy="7"
      r="4"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
    />
  </svg>
);

const BottomNavBar = ({ activeTab, onTabChange }) => {
  const navItems = [
    {
      id: 'orders',
      label: 'Заказы',
      icon: OrdersIcon,
      route: '/orders'
    },
    {
      id: 'products',
      label: 'Товары',
      icon: ProductsIcon,
      route: '/products'
    },
    {
      id: 'warehouse',
      label: 'Склад',
      icon: WarehouseIcon,
      route: '/warehouse'
    },
    {
      id: 'clients',
      label: 'Клиенты',
      icon: ClientsIcon,
      route: '/clients'
    },
    {
      id: 'profile',
      label: 'Профиль',
      icon: ProfileIcon,
      route: '/profile'
    }
  ];

  return (
    <div className="fixed bottom-0 left-1/2 transform -translate-x-1/2 w-[320px] bg-white h-16 shadow-[0px_1px_1px_0px_rgba(0,0,0,0.14),0px_2px_1px_0px_rgba(0,0,0,0.12),0px_1px_3px_0px_rgba(0,0,0,0.2)] z-50">
      <div className="flex h-full">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id, item.route)}
              className="flex-1 flex flex-col items-center justify-center gap-1 py-2"
            >
              <IconComponent isActive={isActive} />
              <span
                className={`text-[10px] font-['Open_Sans'] font-semibold leading-normal ${
                  isActive ? 'text-purple-primary' : 'text-gray-disabled'
                }`}
                style={{ fontVariationSettings: "'wdth' 100" }}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default BottomNavBar;
