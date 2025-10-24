import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchToggle from '../components/SearchToggle';
import SearchInput from '../components/SearchInput';
import BottomNavBar from '../components/BottomNavBar';
import { ordersAPI, formatOrderForDisplay } from '../services';
import '../App.css';

// Правильные изображения букетов из Figma
const imgRectangle = "https://s3-alpha-sig.figma.com/img/d4d9/54b8/cb8a5c7b807046d49f7e09b0f80ca5d3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=jlb4b08XVwrod-dsiaCfPnduD7EFsfgOucqFRo3TNsE758kJ7wc2ypErXx~p1KeLb1QyXSOTDgLIpHtPaaJQaeuovLPxDvu3usc3VUmBOQgLoVDqgAIE8jFr9Dy-AeVBwA68rRLi~aA9fU3CvrukN6v2Pe4KLW-TylZ3s-ETvs5J53p8EPK-rDOja6gd9FN8Q4duU0T6wjVKIzYjoBBuCTm7UA-KSCdwYEqICpFMEzIIMQ-hSdjmhXkyMDZMi04s-R7YQTKtOemKmiGmyrkM9YfzsrPv88KL9QZ1ik5iFBTGKNWOCxYFueW01GS9bMzgYN~gbmRKJuCpcUV2xMp37A__";
const imgRectangle1 = "https://s3-alpha-sig.figma.com/img/6ac5/fd2f/59330fdd9f8b4e0196fdeb1e357e80e3?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=oFyKh7nrZj~6-XDIPvg4k4uWu2KIRgvi~q9rL5S~HsDdAw9qbJJrGCtWuPobF6VLKi5TGJruMMQ~oqxNlyQnN-jrw8zlRdj2kHv8bPBYB61PP9mdF~SiI9fpxinJYp~In5v07JJKjN-KwMIln3kBvyDBPtXsclu8ElbRf2JQhDmqViGf5ng8e9RrXH4FCVVtt08rJm1a0xQqL1HwkoecuYmFdQuOHaYONGwG1oqyak9W4ySoM50QjxT1cigeQPtBULOURGOz~iAVL3fHDYNPckDtlWImq7GUV1zic7oBTwVGYPhll6ONfPiEzKumxKo3m9xFJExYyEvxBP4FNe5b3A__";
const imgRectangle2 = "https://s3-alpha-sig.figma.com/img/9407/eaaf/09bc0cd0735147c984706db31a71bf86?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=ZcUeI1p2PVhMbX3i9N-PWBbsiy8bea6nrc4JfagIE1NVkzuPa~-NYksSPPYlSLvgQRnAu2roiYrlV8szvC8sVZhCTEjCWqHtgqxxpNfGzbrJMOP1SOiaG4EUtRH0kLIuxYeGVnG29c2UPbvOxzMbZ0LTclLvBcDbZ9IFeM53ocnSUXiTS-Pr0VfzE6uIZHegW8wdWALH8Xkvxagnw~D6YwxO~DHzYoUv37ryhBX37hfC2NVEBYsMoBWCEUfqW-EI8zu-E9lKQ9S0LuDo~U7pBQGvm6OshQfOo4yA0HjVT1GCJ8Ah~h~5tZOgfFKzzBRbXmzXvBVOQ7JI~jbVIdhDGQ__";
const imgRectangle3 = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__";

const OrdersAdmin = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  // Fetch orders from Bitrix API
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const params = {
          limit: 50,
          ...(statusFilter !== 'all' && { status: statusFilter })
        };

        // Bitrix API returns { orders: [...], pagination: {...} }
        const response = await ordersAPI.getOrders(params);

        // Use orders from getOrders directly - they already have executors
        // formatOrderForDisplay is already applied by getOrders now
        const enrichedOrders = response.orders;

        console.log('Orders being set:', enrichedOrders);
        if (enrichedOrders.length > 0) {
          console.log('First order:', enrichedOrders[0]);
          console.log('First order executors:', enrichedOrders[0]?.executors);
          console.log('First order executors length:', enrichedOrders[0]?.executors?.length);
        }
        setOrders(enrichedOrders);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch orders:', err);
        setError(err.message || 'Не удалось загрузить заказы');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [statusFilter]);

  const getStatusColor = (status) => {
    const colorMap = {
      'NEW': '#eb5757',
      'PAID': '#5e81dc',
      'ACCEPTED': '#dc5ec0',
      'IN_PRODUCTION': '#f8c20b',
      'IN_DELIVERY': '#7fc663',
      'DELIVERED': '#848484',
    };

    const bgColor = colorMap[status?.toUpperCase()] || '#848484';
    return {
      backgroundColor: bgColor,
      color: 'white',
    };
  };

  // Get action button for order based on status
  const getActionButton = (order) => {
    const status = order.status?.toUpperCase();
    switch (status) {
      case 'NEW':
        return { label: 'Оплачен', newStatus: 'PAID', isPhotoButton: false };
      case 'PAID':
        return { label: 'Принять', newStatus: 'ACCEPTED', isPhotoButton: false };
      case 'ACCEPTED':
        return { label: '+ Фото', newStatus: null, isPhotoButton: true };
      case 'IN_PRODUCTION':
        return { label: '→ Курьеру', newStatus: 'IN_DELIVERY', isPhotoButton: false };
      case 'IN_DELIVERY':
        return { label: 'Завершить', newStatus: 'DELIVERED', isPhotoButton: false };
      default:
        return null;
    }
  };

  // Handle status update
  const handleStatusUpdate = async (order, newStatus) => {
    try {
      await ordersAPI.updateOrderStatus(order.id, newStatus);
      // Refresh orders list
      setStatusFilter(statusFilter);
    } catch (err) {
      console.error('Failed to update order status:', err);
      alert('Ошибка при обновлении статуса');
    }
  };

  // Get photos from order items (up to 4)
  // Support both formats: raw.basket and items array
  const getOrderPhotos = (order) => {
    let items = [];

    // Try raw.basket first (Bitrix format)
    if (order.raw?.basket && Array.isArray(order.raw.basket)) {
      items = order.raw.basket.map(item => item.productImage).filter(img => img);
    }
    // Fallback to order.items
    else if (order.items && Array.isArray(order.items)) {
      items = order.items.map(item => item.image).filter(img => img);
    }

    return items.slice(0, 4);
  };

  // Get initials from name for avatar
  const getInitials = (name) => {
    if (!name) return '?';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Get color for avatar background (deterministic based on name)
  const getAvatarColor = (name) => {
    const colors = ['#8a49f3', '#f8c20b', '#dc5ec0', '#7fc663', '#5e81dc', '#eb5757'];
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) {
      hash = ((hash << 5) - hash) + (name || '').charCodeAt(i);
      hash = hash & hash;
    }
    return colors[Math.abs(hash) % colors.length];
  };

  // Get executor avatars and tags from order data
  const getExecutorAvatars = (order) => {
    const avatars = [];

    if (order.executors && Array.isArray(order.executors)) {
      order.executors.forEach(executor => {
        if (executor.name && !avatars.find(a => a.name === executor.name)) {
          avatars.push({
            name: executor.name,
            initials: getInitials(executor.name),
            color: getAvatarColor(executor.name),
            source: executor.source || 'Cvety.kz'
          });
        }
      });
    }

    return avatars;
  };

  // Get executor tags from order data
  // Executors could be florist and/or courier
  const getExecutorTags = (order) => {
    const tags = [];

    if (order.executors && Array.isArray(order.executors)) {
      order.executors.forEach(executor => {
        if (executor.name) {
          const tag = executor.source ? `${executor.name} с ${executor.source}` : executor.name;
          if (!tags.find(t => t === tag)) {
            tags.push(tag);
          }
        }
      });
    }

    return tags;
  };

  const statusFilters = [
    { id: 'all', label: 'Все' },
    { id: 'new', label: 'Новые' },
    { id: 'paid', label: 'Оплаченные' },
    { id: 'accepted', label: 'Принятые' },
    { id: 'assembled', label: 'Собранные' }
  ];

  // Filter orders by search query only (status filter applied at API level)
  const filteredOrders = React.useMemo(() => {
    let filtered = orders;

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(order =>
        order.customerName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        order.orderNumber?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        order.phone?.includes(searchQuery)
      );
    }

    return filtered;
  }, [orders, searchQuery]);

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

  const handleNavChange = (navId, route) => {
    navigate(route);
  };

  return (
    <div className="figma-container bg-white">

      {/* Segmented Control - Tabs */}
      <div className="flex h-[34px] rounded overflow-hidden w-full mt-4">
        <button className="flex-1 bg-purple-primary text-white text-[14px] font-sans flex items-center justify-center">
          Заказы
        </button>
        <button className="flex-1 bg-white text-purple-primary text-[14px] font-sans flex items-center justify-center">
          Дашборд
        </button>
      </div>

      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-sans font-normal">Заказы</h1>
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

      {/* Filter Pills - Status */}
      <div className="flex gap-2 px-4 mt-6 overflow-x-auto">
        {statusFilters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setStatusFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[16px] font-sans font-normal whitespace-nowrap ${
              statusFilter === filter.id
                ? 'bg-purple-primary text-white'
                : 'bg-violet-light text-black'
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

      {/* Error state */}
      {error && (
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

            {/* Order Item - Pixel Perfect Figma Layout */}
            <div className="px-4 py-4 hover:bg-gray-50 transition-colors">
              {/* Main Grid Layout: Avatars | Info | Status/Button | Tags */}
              <div className="grid grid-cols-[80px_1fr_120px] gap-4 items-start">
                {/* LEFT: Overlapping Executor Avatars */}
                <div className="relative" style={{ height: '48px', width: '80px' }}>
                  {getExecutorAvatars(order).slice(0, 4).map((avatar, idx) => (
                    <div
                      key={idx}
                      className="w-12 h-12 rounded-full border-2 border-white flex items-center justify-center text-white text-[13px] font-sans font-bold absolute"
                      style={{
                        backgroundColor: avatar.color,
                        left: `${idx * 16}px`,
                        top: 0,
                        zIndex: 4 - idx
                      }}
                      title={avatar.name}
                    >
                      {avatar.initials}
                    </div>
                  ))}

                  {/* "+N" badge if more than 4 executors */}
                  {getExecutorAvatars(order).length > 4 && (
                    <div
                      className="w-12 h-12 rounded-full border-2 border-white flex items-center justify-center text-white text-[12px] font-sans font-semibold absolute"
                      style={{
                        backgroundColor: '#8a49f3',
                        left: `${4 * 16}px`,
                        top: 0,
                        zIndex: 0
                      }}
                    >
                      +{getExecutorAvatars(order).length - 4}
                    </div>
                  )}
                </div>

                {/* CENTER: Order Information */}
                <div
                  className="flex flex-col justify-start cursor-pointer min-h-[48px]"
                  onClick={() => navigate(`/orders/${order.id}`)}
                >
                  {/* Order Number + Status */}
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-[16px] font-sans font-bold text-black">
                      {order.orderNumber || `#${order.id}`}
                    </h3>
                  </div>

                  {/* Address - First line only */}
                  <p className="text-[14px] font-sans text-black leading-snug truncate mb-0.5">
                    {order.delivery_address?.split(',')[0] || order.customerName || 'Заказ'}
                  </p>

                  {/* Date + Time */}
                  <p className="text-[13px] font-sans text-gray-placeholder leading-snug">
                    {order.delivery_date}
                  </p>
                </div>

                {/* RIGHT: Status Badge + Action Button */}
                <div className="flex flex-col items-end justify-start gap-2 min-h-[48px]">
                  {/* Status Badge */}
                  <span
                    style={{...getStatusColor(order.status)}}
                    className="px-2 py-1 rounded-full text-[11px] font-sans font-normal uppercase tracking-[0.5px] whitespace-nowrap"
                  >
                    {order.statusLabel}
                  </span>

                  {/* Action Button */}
                  {getActionButton(order) && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const action = getActionButton(order);
                        if (action.isPhotoButton) {
                          navigate(`/orders/${order.id}`);
                        } else if (action.newStatus) {
                          handleStatusUpdate(order, action.newStatus);
                        }
                      }}
                      className="px-3 py-1.5 rounded text-[12px] font-sans font-normal text-black border border-gray-border bg-white hover:bg-gray-50 whitespace-nowrap transition-colors"
                    >
                      {getActionButton(order).label}
                    </button>
                  )}
                </div>
              </div>

              {/* BOTTOM ROW: Executor Tags */}
              {getExecutorTags(order).length > 0 && (
                <div className="flex gap-2 flex-wrap mt-3 ml-[80px]">
                  {getExecutorTags(order).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-violet-light text-black text-[11px] font-sans font-normal rounded-full whitespace-nowrap uppercase tracking-[0.5px]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
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
        activeTab="orders"
        onTabChange={handleNavChange}
      />
    </div>
  );
};

export default OrdersAdmin;
