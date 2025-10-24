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

  // Get photos from order (use real API data)
  const getOrderPhotos = (order) => {
    // 1. First priority: itemImages from API (all product images)
    if (order.itemImages && Array.isArray(order.itemImages) && order.itemImages.length > 0) {
      return order.itemImages.slice(0, 4);
    }

    // 2. Second priority: mainImage from API
    if (order.mainImage) {
      return [order.mainImage];
    }

    // 3. Third priority: images from order items (for detail page)
    if (order.items && Array.isArray(order.items)) {
      const itemPhotos = order.items
        .map(item => item.image || item.image_big || item.productImage)
        .filter(img => img);
      if (itemPhotos.length > 0) {
        return itemPhotos.slice(0, 4);
      }
    }

    // 4. Fallback: placeholder images
    return [imgRectangle3, imgRectangle2, imgRectangle1, imgRectangle];
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
    <div className="figma-container bg-white relative">

      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-[22px]">
        <h1 className="text-[24px] font-sans font-normal">Заказы</h1>
        <div className="flex items-center gap-4">
          {/* Calendar icon */}
          <button className="w-6 h-6 flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="4" y="5" width="16" height="16" rx="2" stroke="black" strokeWidth="1.5"/>
              <line x1="16" y1="3" x2="16" y2="7" stroke="black" strokeWidth="1.5"/>
              <line x1="8" y1="3" x2="8" y2="7" stroke="black" strokeWidth="1.5"/>
              <line x1="4" y1="9" x2="20" y2="9" stroke="black" strokeWidth="1.5"/>
            </svg>
          </button>

          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск по заказам"
            enabled={orders.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
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

            {/* Order Item - Figma Pixel-Perfect Layout */}
            <div className="px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => navigate(`/orders/${order.id}`)}>
              {/* Row 1: Order Number (left) + Status Badge (right) */}
              <div className="flex items-start justify-between mb-1">
                <h3 className="text-[16px] font-sans font-bold text-black">
                  {order.orderNumber || `#${order.id}`}
                </h3>
                <span
                  style={{...getStatusColor(order.status)}}
                  className="px-[6px] py-[3px] rounded-[21px] text-[12px] font-sans font-normal uppercase tracking-[1.2px] whitespace-nowrap"
                >
                  {order.statusLabel}
                </span>
              </div>

              {/* Row 2: Recipient Name + WhatsApp Button */}
              <div className="flex items-center gap-2 mb-1">
                <p className="text-[16px] font-sans text-black">
                  {order.recipient?.name || order.customerName || 'Получатель не указан'}
                </p>
                {order.recipient?.phone && (
                  <a
                    href={`https://wa.me/${order.recipient.phone.replace(/[^0-9]/g, '')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center justify-center w-6 h-6 bg-[#25D366] rounded-full hover:bg-[#1ebe57] transition-colors"
                    title="Написать в WhatsApp"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                    </svg>
                  </a>
                )}
              </div>

              {/* Row 3: Delivery Address */}
              {order.delivery_address && (
                <p className="text-[14px] font-sans text-gray-500 mb-1 truncate">
                  📍 {order.delivery_address}
                </p>
              )}

              {/* Row 4: Delivery Time + Order Total */}
              <p className="text-[16px] font-sans text-black mb-3">
                {order.delivery_date || 'Время не указано'} • {order.total || '0 ₸'}
              </p>

              {/* Row 5: Executor Tags */}
              {getExecutorTags(order).length > 0 && (
                <div className="flex gap-2 flex-wrap mb-3">
                  {getExecutorTags(order).map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-[6px] py-[3px] bg-[#EFEBF6] text-black text-[12px] font-sans font-normal rounded-[21px] uppercase tracking-[1.2px]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Row 6: Overlapping Images + Action Button */}
              <div className="flex items-center justify-between">
                {/* Overlapping Images - pixel-perfect positioning */}
                <div className="relative h-[48px] flex-1">
                  {getOrderPhotos(order).map((photo, idx) => {
                    // Pixel-perfect positioning from Figma
                    const positions = [
                      'left-[0px]',      // First image
                      'left-[32px]',     // Second at +32px
                      'left-[64px]',     // Third at +64px
                      'left-[96px]'      // Fourth at +96px
                    ];

                    return (
                      <div
                        key={idx}
                        className={`absolute ${positions[idx]} w-[48px] h-[48px] rounded-full border-2 border-white overflow-hidden`}
                        style={{ zIndex: 4 - idx }}
                      >
                        <img
                          src={photo}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      </div>
                    );
                  })}

                  {/* "+N more" badge if more than 4 items */}
                  {order.items && order.items.length > 4 && (
                    <div
                      className="absolute left-[128px] w-[48px] h-[48px] rounded-full bg-purple-primary border-2 border-white flex items-center justify-center text-white font-sans font-semibold text-[16px]"
                      style={{ zIndex: 0 }}
                    >
                      +{order.items.length - 4}
                    </div>
                  )}
                </div>

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
                    className="ml-4 px-4 h-[38px] bg-white border border-[#E2E2E2] rounded-[4px] text-[16px] font-sans font-normal text-black hover:bg-gray-50 transition-colors whitespace-nowrap"
                  >
                    {getActionButton(order).label}
                  </button>
                )}
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
        activeTab="orders"
        onTabChange={handleNavChange}
      />
    </div>
  );
};

export default OrdersAdmin;
