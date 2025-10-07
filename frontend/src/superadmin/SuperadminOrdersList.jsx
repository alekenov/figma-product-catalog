import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { orderAPI } from '../api/superadmin';
import BottomNavBar from '../components/BottomNavBar';
import SearchToggle from '../components/SearchToggle';
import SearchInput from '../components/SearchInput';
import '../App.css';

const SuperadminOrdersList = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [shopFilter, setShopFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch orders from API
  useEffect(() => {
    fetchOrders();
  }, [shopFilter, statusFilter]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100
      };

      if (shopFilter) {
        params.shop_id = parseInt(shopFilter);
      }

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      const data = await orderAPI.list(params);
      setOrders(data);
      setError(null);
      setIsAuthError(false);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
      const isAuthMsg = err.message?.includes('Сессия истекла') ||
                        err.message?.includes('Необходима авторизация') ||
                        err.message?.includes('Недостаточно прав');
      setIsAuthError(isAuthMsg);
      setError(err.message || 'Не удалось загрузить заказы');
    } finally {
      setLoading(false);
    }
  };

  // Filter orders by search query
  const filteredOrders = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return orders;
    }

    return orders.filter(order =>
      order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.phone?.includes(searchQuery) ||
      order.shop_name?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [orders, searchQuery]);

  // Format price in tenge
  const formatPrice = (price) => {
    return (price / 100).toLocaleString('ru-RU', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'new':
        return 'bg-status-new text-white';
      case 'paid':
        return 'bg-status-blue text-white';
      case 'accepted':
        return 'bg-status-pink text-white';
      case 'assembled':
        return 'bg-status-assembled text-white';
      case 'in_delivery':
        return 'bg-status-green text-white';
      case 'delivered':
        return 'bg-green-success text-white';
      case 'cancelled':
        return 'bg-gray-400 text-white';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get status label
  const getStatusLabel = (status) => {
    const statusLabels = {
      'new': 'Новый',
      'paid': 'Оплачен',
      'accepted': 'Принят',
      'assembled': 'Собран',
      'in_delivery': 'В пути',
      'delivered': 'Доставлен',
      'cancelled': 'Отменён'
    };
    return statusLabels[status] || status;
  };

  const statusFilters = [
    { id: 'all', label: 'Все заказы' },
    { id: 'new', label: 'Новые' },
    { id: 'paid', label: 'Оплаченные' },
    { id: 'accepted', label: 'Принятые' },
    { id: 'assembled', label: 'Собранные' },
    { id: 'in_delivery', label: 'В доставке' },
    { id: 'delivered', label: 'Доставленные' },
    { id: 'cancelled', label: 'Отменённые' }
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
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">Заказы</h1>
        </div>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск заказов"
            enabled={orders.length > 0}
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
          placeholder="Поиск по клиенту, телефону или магазину"
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

      {/* Shop Filter Input */}
      <div className="px-4 mt-4">
        <input
          type="number"
          placeholder="Фильтр по ID магазина"
          value={shopFilter}
          onChange={(e) => setShopFilter(e.target.value)}
          className="w-full px-3 py-2 border border-gray-border rounded-lg text-[14px] font-['Open_Sans'] focus:outline-none focus:border-purple-primary"
        />
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка заказов...</div>
        </div>
      )}

      {/* Auth error */}
      {error && isAuthError && (
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            Войдите в систему, чтобы увидеть заказы
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
            onClick={fetchOrders}
            className="bg-purple-primary text-white px-4 py-2 rounded-lg font-['Open_Sans'] text-sm"
          >
            Повторить
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredOrders.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Заказы не найдены' : 'Заказов пока нет'}
          </div>
        </div>
      )}

      {/* Orders count */}
      {!loading && !error && filteredOrders.length > 0 && (
        <div className="px-4 mt-6 mb-2">
          <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
            Найдено заказов: {filteredOrders.length}
          </span>
        </div>
      )}

      {/* Orders List */}
      <div className="mt-2">
        {!loading && !error && filteredOrders.map((order) => (
          <div key={order.id}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Order Item */}
            <div className="px-4 py-4 cursor-pointer hover:bg-gray-50"
                 onClick={() => navigate(`/superadmin/orders/${order.id}`)}>
              <div className="flex items-start justify-between gap-4">
                {/* Order Info */}
                <div className="flex-1">
                  {/* Order Number and Status */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      Заказ #{order.id}
                    </h3>
                    <span className={`px-2 py-1 rounded text-[12px] font-['Open_Sans'] font-normal uppercase tracking-wide ${getStatusColor(order.status)}`}>
                      {getStatusLabel(order.status)}
                    </span>
                  </div>

                  {/* Customer Name */}
                  <p className="text-[16px] font-['Open_Sans'] text-black mb-1">
                    {order.customerName}
                  </p>

                  {/* Phone */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    {order.phone}
                  </p>

                  {/* Shop Name */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    <span className="font-semibold">Магазин:</span> {order.shop_name} (ID: {order.shop_id})
                  </p>

                  {/* Date */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    {formatDate(order.created_at)}
                  </p>
                </div>

                {/* Order Total */}
                <div className="text-right">
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {formatPrice(order.total)} ₸
                  </p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    {order.items?.length || 0} поз.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {!loading && !error && filteredOrders.length > 0 && (
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

export default SuperadminOrdersList;
