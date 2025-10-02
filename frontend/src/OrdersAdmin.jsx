import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import { ordersAPI, formatOrderForDisplay } from './services/api';
import './App.css';

// Правильные изображения букетов из Figma
const imgRectangle = "https://s3-alpha-sig.figma.com/img/d4d9/54b8/cb8a5c7b807046d49f7e09b0f80ca5d3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=jlb4b08XVwrod-dsiaCfPnduD7EFsfgOucqFRo3TNsE758kJ7wc2ypErXx~p1KeLb1QyXSOTDgLIpHtPaaJQaeuovLPxDvu3usc3VUmBOQgLoVDqgAIE8jFr9Dy-AeVBwA68rRLi~aA9fU3CvrukN6v2Pe4KLW-TylZ3s-ETvs5J53p8EPK-rDOja6gd9FN8Q4duU0T6wjVKIzYjoBBuCTm7UA-KSCdwYEqICpFMEzIIMQ-hSdjmhXkyMDZMi04s-R7YQTKtOemKmiGmyrkM9YfzsrPv88KL9QZ1ik5iFBTGKNWOCxYFueW01GS9bMzgYN~gbmRKJuCpcUV2xMp37A__";
const imgRectangle1 = "https://s3-alpha-sig.figma.com/img/6ac5/fd2f/59330fdd9f8b4e0196fdeb1e357e80e3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=oFyKh7nrZj~6-XDIPvg4k4uWu2KIRgvi~q9rL5S~HsDdAw9qbJJrGCtWuPobF6VLKi5TGJruMMQ~oqxNlyQnN-jrw8zlRdj2kHv8bPBYB61PP9mdF~SiI9fpxinJYp~In5v07JJKjN-KwMIln3kBvyDBPtXsclu8ElbRf2JQhDmqViGf5ng8e9RrXH4FCVVtt08rJm1a0xQqL1HwkoecuYmFdQuOHaYONGwG1oqyak9W4ySoM50QjxT1cigeQPtBULOURGOz~iAVL3fHDYNPckDtlWImq7GUV1zic7oBTwVGYPhll6ONfPiEzKumxKo3m9xFJExYyEvxBP4FNe5b3A__";
const imgRectangle2 = "https://s3-alpha-sig.figma.com/img/9407/eaaf/09bc0cd0735147c984706db31a71bf86?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=ZcUeI1p2PVhMbX3i9N-PWBbsiy8bea6nrc4JfagIE1NVkzuPa~-NYksSPPYlSLvgQRnAu2roiYrlV8szvC8sVZhCTEjCWqHtgqxxpNfGzbrJMOP1SOiaG4EUtRH0kLIuxYeGVnG29c2UPbvOxzMbZ0LTclLvBcDbZ9IFeM53ocnSUXiTS-Pr0VfzE6uIZHegW8wdWALH8Xkvxagnw~D6YwxO~DHzYoUv37ryhBX37hfC2NVEBYsMoBWCEUfqW-EI8zu-E9lKQ9S0LuDo~U7pBQGvm6OshQfOo4yA0HjVT1GCJ8Ah~h~5tZOgfFKzzBRbXmzXvBVOQ7JI~jbVIdhDGQ__";
const imgRectangle3 = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__";

const OrdersAdmin = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('orders');
  const [activeTab, setActiveTab] = useState('orders'); // orders or dashboard
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

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
        // Check if it's an auth error
        const isAuthMsg = err.message?.includes('Сессия истекла') ||
                          err.message?.includes('Необходима авторизация') ||
                          err.message?.includes('Недостаточно прав');
        setIsAuthError(isAuthMsg);
        setError(err.message || 'Не удалось загрузить заказы');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

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
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const statusFilters = [
    { id: 'all', label: 'Все' },
    { id: 'new', label: 'Новые' },
    { id: 'paid', label: 'Оплаченные' },
    { id: 'accepted', label: 'Принятые' },
    { id: 'assembled', label: 'Собранные' }
  ];

  // Filter orders by status and search query
  const filteredOrders = React.useMemo(() => {
    let filtered = orders;

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(order =>
        order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        order.orderNumber?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        order.phone?.includes(searchQuery)
      );
    }

    return filtered;
  }, [orders, statusFilter, searchQuery]);

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

      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-[24px] font-['Open_Sans'] font-normal">Заказы</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск по заказам"
            enabled={orders.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
          {/* Calendar icon */}
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" strokeWidth="2"/>
            <line x1="16" y1="2" x2="16" y2="6" strokeWidth="2"/>
            <line x1="8" y1="2" x2="8" y2="6" strokeWidth="2"/>
            <line x1="3" y1="10" x2="21" y2="10" strokeWidth="2"/>
          </svg>
          {/* Add button */}
          <button
            onClick={() => navigate('/create-order')}
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
            <span className="text-white text-lg leading-none">+</span>
          </button>
        </div>
      </div>

      {/* Search Input Row - Shows below header when expanded */}
      {isSearchExpanded && (
        <SearchInput
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          placeholder="Поиск по заказам"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Status Filter Pills */}
      <div className="flex gap-2 px-4 mt-6 overflow-x-auto">
        {statusFilters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setStatusFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[16px] font-['Open_Sans'] font-normal whitespace-nowrap ${
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
          <div className="text-gray-placeholder">Загрузка заказов...</div>
        </div>
      )}

      {/* Auth error - friendly prompt */}
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

      {/* Other errors - soft message */}
      {error && !isAuthError && (
        <div className="flex flex-col justify-center items-center py-8 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-2">
            Не удалось загрузить данные
          </div>
          <div className="text-gray-400 text-sm">
            {error}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredOrders.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Заказы не найдены' : orders.length === 0 ? 'Заказов пока нет' : 'Нет заказов с выбранными фильтрами'}
          </div>
        </div>
      )}

      {/* Orders List */}
      <div className="mt-6">
        {!loading && !error && filteredOrders.map((order, index) => (
          <div key={order.id}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Order Item */}
            <div className="px-4 py-4 cursor-pointer hover:bg-gray-50" onClick={() => navigate(`/orders/${order.id}`)}>
              <div className="flex items-start justify-between">
                {/* Order Info */}
                <div className="flex-1">
                  {/* Order Number and Status */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {order.orderNumber}
                    </h3>
                    <span className={`px-[6px] py-[3px] rounded-[21px] text-[12px] font-['Open_Sans'] font-normal uppercase tracking-[1.2px] ${getStatusColor(order.status)}`}>
                      {order.statusLabel}
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

                  {/* Date */}
                  <p className="text-[16px] font-['Open_Sans'] text-black mb-3">
                    {order.date} в {order.time}
                  </p>

                  {/* Tags if present */}
                  {order.tags && (
                    <div className="flex gap-2 mb-3">
                      {order.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-[6px] py-[3px] bg-purple-light text-black text-[12px] font-['Open_Sans'] font-normal rounded-full uppercase tracking-[1.2px]"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Order Total */}
                <div className="text-right ml-4">
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {order.total}
                  </p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    {order.items.length} поз.
                  </p>
                </div>
              </div>

              {/* Product Photos Row - как в оригинальном дизайне */}
              <div className="flex items-center mt-3 relative">
                {/* Показываем до 4 фото товаров */}
                {[imgRectangle3, imgRectangle, imgRectangle1, imgRectangle2].slice(0, Math.min(4, order.items?.length || 4)).map((avatar, idx) => (
                  <div
                    key={idx}
                    className="w-12 h-12 rounded-full border-2 border-white overflow-hidden relative"
                    style={{ marginLeft: idx > 0 ? '-8px' : '0', zIndex: 4 - idx }}
                  >
                    <img
                      src={avatar}
                      alt=""
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
                {/* Если товаров больше 4, показываем счетчик */}
                {order.items && order.items.length > 4 && (
                  <div className="w-12 h-12 rounded-full bg-purple-primary border-2 border-white flex items-center justify-center text-white font-['Open_Sans'] font-semibold text-[16px] -ml-2 relative"
                       style={{ zIndex: 0 }}>
                    +{order.items.length - 4}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        <div className="border-t border-gray-border"></div>
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

export default OrdersAdmin;