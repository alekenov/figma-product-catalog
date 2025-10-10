import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { statsAPI } from './api/superadmin';
import BottomNavBar from './components/BottomNavBar';
import './App.css';

const Superadmin = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch platform statistics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await statsAPI.getPlatformStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        setError(err.message || 'Не удалось загрузить статистику');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const menuItems = [
    {
      title: 'Магазины',
      description: 'Управление магазинами платформы',
      route: '/superadmin/shops',
      icon: '🏪',
      stats: stats ? `${stats.shops?.total || 0} магазинов` : null
    },
    {
      title: 'Пользователи',
      description: 'Управление пользователями',
      route: '/superadmin/users',
      icon: '👥',
      stats: stats ? `${stats.users?.total || 0} пользователей` : null
    },
    {
      title: 'Товары',
      description: 'Просмотр всех товаров на платформе',
      route: '/superadmin/products',
      icon: '📦',
      stats: stats ? `${stats.products?.total || 0} товаров` : null
    },
    {
      title: 'Заказы',
      description: 'Просмотр всех заказов на платформе',
      route: '/superadmin/orders',
      icon: '📋',
      stats: stats ? `${stats.orders?.total || 0} заказов` : null
    },
    {
      title: 'Чаты AI агента',
      description: 'Мониторинг чатов с AI ботом',
      route: '/superadmin/chats',
      icon: '💬',
      stats: null
    }
  ];

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="px-4 mt-5 mb-6">
        <h1 className="text-[28px] font-['Open_Sans'] font-bold mb-2">
          🛡️ Суперадминистратор
        </h1>
        <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
          Управление платформой Figma Product Catalog
        </p>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка статистики...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="mx-4 mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 text-[14px] font-['Open_Sans']">{error}</p>
        </div>
      )}

      {/* Statistics Cards */}
      {!loading && stats && (
        <div className="mx-4 mb-6 bg-purple-light rounded-xl p-4">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">
            Статистика платформы
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {/* Shops stat */}
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-purple-primary">
                {stats.shops?.total || 0}
              </div>
              <div className="text-[13px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Всего магазинов
              </div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-400 mt-0.5">
                Активных: {stats.shops?.active || 0}
              </div>
            </div>

            {/* Users stat */}
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-green-success">
                {stats.users?.total || 0}
              </div>
              <div className="text-[13px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Всего пользователей
              </div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-400 mt-0.5">
                Активных: {stats.users?.active || 0}
              </div>
            </div>

            {/* Products stat */}
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-status-pink">
                {stats.products?.total || 0}
              </div>
              <div className="text-[13px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Всего товаров
              </div>
            </div>

            {/* Orders stat */}
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-status-blue">
                {stats.orders?.total || 0}
              </div>
              <div className="text-[13px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Всего заказов
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Menu Items */}
      <div className="px-4">
        {menuItems.map((item, index) => (
          <div key={index}>
            {/* Divider */}
            {index > 0 && <div className="border-t border-gray-border"></div>}

            {/* Menu Item */}
            <button
              onClick={() => navigate(item.route)}
              className="w-full py-4 flex items-center gap-4 text-left hover:bg-purple-light transition-colors"
            >
              <div className="text-3xl">
                {item.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-[18px] font-['Open_Sans'] font-semibold text-black mb-1">
                  {item.title}
                </h3>
                <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                  {item.description}
                </p>
                {item.stats && (
                  <p className="text-[12px] font-['Open_Sans'] text-gray-400 mt-1">
                    {item.stats}
                  </p>
                )}
              </div>
              <div className="text-xl text-gray-border">
                →
              </div>
            </button>
          </div>
        ))}

        {/* Final divider */}
        <div className="border-t border-gray-border"></div>
      </div>

      {/* Logout button */}
      <div className="px-4 mt-6 text-center">
        <button
          onClick={() => {
            localStorage.removeItem('token');
            navigate('/login');
          }}
          className="bg-red-500 text-white px-6 py-2 rounded-lg text-[14px] font-['Open_Sans'] font-normal hover:bg-red-600 transition-colors"
        >
          Выйти
        </button>
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-16" />

      {/* Bottom Navigation */}
      <BottomNavBar
        activeTab={activeNav}
        onTabChange={handleNavChange}
      />
    </div>
  );
};

export default Superadmin;
