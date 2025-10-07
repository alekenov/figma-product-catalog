import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { shopAPI } from '../api/superadmin';
import BottomNavBar from '../components/BottomNavBar';
import SearchToggle from '../components/SearchToggle';
import SearchInput from '../components/SearchInput';
import '../App.css';

const ShopsList = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile');
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, active, blocked
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch shops from API
  useEffect(() => {
    fetchShops();
  }, [statusFilter]);

  const fetchShops = async () => {
    try {
      setLoading(true);
      const params = {};

      if (statusFilter === 'active') {
        params.is_active = true;
      } else if (statusFilter === 'blocked') {
        params.is_active = false;
      }

      const data = await shopAPI.list(params);
      setShops(data);
      setError(null);
      setIsAuthError(false);
    } catch (err) {
      console.error('Failed to fetch shops:', err);
      const isAuthMsg = err.message?.includes('Сессия истекла') ||
                        err.message?.includes('Необходима авторизация') ||
                        err.message?.includes('Недостаточно прав');
      setIsAuthError(isAuthMsg);
      setError(err.message || 'Не удалось загрузить магазины');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleShop = async (shop) => {
    try {
      if (shop.is_active) {
        await shopAPI.block(shop.id);
      } else {
        await shopAPI.unblock(shop.id);
      }
      await fetchShops();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  // Filter shops by search query
  const filteredShops = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return shops;
    }

    return shops.filter(shop =>
      shop.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      shop.city?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      shop.phone?.includes(searchQuery)
    );
  }, [shops, searchQuery]);

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const statusFilters = [
    { id: 'all', label: 'Все магазины' },
    { id: 'active', label: 'Активные' },
    { id: 'blocked', label: 'Заблокированные' }
  ];

  // Handle search expanded state
  useEffect(() => {
    if (isSearchExpanded && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [isSearchExpanded]);

  // Auto-expand search if there's a query
  useEffect(() => {
    if (searchQuery.trim()) {
      setIsSearchExpanded(true);
    }
  }, [searchQuery]);

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/superadmin')}
            className="text-black text-xl"
          >
            ←
          </button>
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">Магазины</h1>
        </div>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск магазинов"
            enabled={shops.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
        </div>
      </div>

      {/* Search Input Row */}
      {isSearchExpanded && (
        <SearchInput
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          placeholder="Поиск по названию, городу или телефону"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Status Filter Pills */}
      <div className="flex gap-2 px-4 mt-6 overflow-x-auto pb-2">
        {statusFilters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setStatusFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[14px] font-['Open_Sans'] font-normal whitespace-nowrap ${
              statusFilter === filter.id
                ? 'bg-purple-primary text-white'
                : 'bg-purple-light text-black'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка магазинов...</div>
        </div>
      )}

      {/* Auth error */}
      {error && isAuthError && (
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            Войдите в систему, чтобы увидеть магазины
          </div>
          <button
            onClick={() => navigate('/login')}
            className="bg-purple-primary text-white px-6 py-2 rounded-lg font-['Open_Sans'] text-sm hover:bg-purple-600 transition-colors"
          >
            Войти
          </button>
        </div>
      )}

      {/* Other errors */}
      {error && !isAuthError && (
        <div className="flex flex-col justify-center items-center py-8 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-2">
            Не удалось загрузить данные
          </div>
          <div className="text-gray-400 text-sm mb-4">
            {error}
          </div>
          <button
            onClick={fetchShops}
            className="bg-purple-primary text-white px-4 py-2 rounded-lg font-['Open_Sans'] text-sm"
          >
            Повторить
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredShops.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Магазины не найдены' : 'Магазинов пока нет'}
          </div>
        </div>
      )}

      {/* Shops count */}
      {!loading && !error && filteredShops.length > 0 && (
        <div className="px-4 mt-6 mb-2">
          <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
            Найдено магазинов: {filteredShops.length}
          </span>
        </div>
      )}

      {/* Shops List */}
      <div className="mt-2">
        {!loading && !error && filteredShops.map((shop) => (
          <div key={shop.id}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Shop Item */}
            <div className="px-4 py-4">
              <div className="flex items-start justify-between gap-4">
                {/* Shop Info */}
                <div className="flex-1 cursor-pointer" onClick={() => navigate(`/superadmin/shops/${shop.id}`)}>
                  {/* Shop Name and Status */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {shop.name}
                    </h3>
                    <span className={`px-2 py-1 rounded text-[12px] font-['Open_Sans'] font-normal uppercase tracking-wide ${
                      shop.is_active
                        ? 'bg-green-success text-white'
                        : 'bg-gray-400 text-white'
                    }`}>
                      {shop.is_active ? 'Активен' : 'Заблокирован'}
                    </span>
                  </div>

                  {/* City */}
                  {shop.city && (
                    <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      <span className="font-semibold">Город:</span> {shop.city}
                    </p>
                  )}

                  {/* Phone */}
                  {shop.phone && (
                    <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      {shop.phone}
                    </p>
                  )}

                  {/* Date */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    Создан: {formatDate(shop.created_at)}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => navigate(`/superadmin/shops/${shop.id}`)}
                    className="px-3 py-1.5 bg-purple-primary text-white rounded-lg text-[13px] font-['Open_Sans'] font-normal whitespace-nowrap"
                  >
                    Детали
                  </button>

                  <button
                    onClick={() => handleToggleShop(shop)}
                    className={`px-3 py-1.5 rounded-lg text-[13px] font-['Open_Sans'] font-normal text-white whitespace-nowrap ${
                      shop.is_active ? 'bg-red-500' : 'bg-green-success'
                    }`}
                  >
                    {shop.is_active ? 'Заблокировать' : 'Разблокировать'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {!loading && !error && filteredShops.length > 0 && (
          <div className="border-t border-gray-border"></div>
        )}
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

export default ShopsList;
