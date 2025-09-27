import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import FilterHeader from './components/FilterHeader';
import { ordersAPI, formatOrderForDisplay } from './services/api';
import './App.css';

const Orders = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('orders');
  const [searchQuery, setSearchQuery] = useState('');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch orders from API
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const rawOrders = await ordersAPI.getOrders({ limit: 50 });
        const formattedOrders = rawOrders.map(formatOrderForDisplay);
        setOrders(formattedOrders);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch orders:', err);
        setError('Не удалось загрузить заказы');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'new':
        return 'bg-blue-100 text-blue-800';
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'accepted':
        return 'bg-purple-100 text-purple-800';
      case 'assembled':
        return 'bg-orange-100 text-orange-800';
      case 'in_delivery':
        return 'bg-yellow-100 text-yellow-800';
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Filter orders based on search
  const filteredOrders = orders.filter(order =>
    order.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.orderNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.phone.includes(searchQuery)
  );

  return (
    <div className="figma-container bg-white">

      {/* Header with Search Toggle */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Заказы</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск по заказам"
            enabled={orders.length > 0}
          />
          {/* Add Order Button */}
          <button
            onClick={() => navigate('/add-order')}
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
            <span className="text-white text-lg leading-none">+</span>
          </button>
        </div>
      </div>

      {/* Filter section using design system */}
      <FilterHeader
        type="orders"
        label="Все заказы"
        onFiltersClick={() => navigate('/order-filters')}
      />

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка заказов...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex justify-center items-center py-8">
          <div className="text-red-500">{error}</div>
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

      {/* Orders List */}
      <div className="mt-6">
        {!loading && !error && filteredOrders.map((order, index) => (
          <div key={order.id}>
            {/* Top border for first item */}
            {index === 0 && (
              <div className="mx-4 border-t border-gray-border"></div>
            )}

            {/* Order Item */}
            <div
              className="px-4 py-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => navigate(`/order/${order.id}`)}
            >
              <div className="flex items-start justify-between">
                {/* Order Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-sm font-['Open_Sans'] font-bold text-black">
                      {order.orderNumber}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-['Open_Sans'] font-medium ${getStatusColor(order.status)}`}>
                      {order.statusLabel}
                    </span>
                  </div>

                  <p className="text-sm font-['Open_Sans'] text-black mb-1">
                    {order.customerName}
                  </p>

                  <p className="text-xs font-['Open_Sans'] text-gray-placeholder mb-1">
                    {order.phone}
                  </p>

                  <p className="text-xs font-['Open_Sans'] text-gray-placeholder">
                    {order.date} в {order.time}
                  </p>
                </div>

                {/* Order Total */}
                <div className="text-right">
                  <p className="text-sm font-['Open_Sans'] font-bold text-black">
                    {order.total}
                  </p>
                  <p className="text-xs font-['Open_Sans'] text-gray-placeholder">
                    {order.items.length} поз.
                  </p>
                </div>
              </div>

              {/* Order Items Preview */}
              <div className="mt-3 pt-3 border-t border-gray-border">
                <div className="text-xs font-['Open_Sans'] text-gray-placeholder">
                  {order.items.map((item, idx) => (
                    <span key={idx}>
                      {item.name} ({item.quantity} шт.)
                      {idx < order.items.length - 1 && ', '}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom border */}
            <div className="mx-4 border-t border-gray-border"></div>
          </div>
        ))}
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

export default Orders;