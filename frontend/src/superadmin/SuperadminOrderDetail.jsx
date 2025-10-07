import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { orderAPI } from '../api/superadmin';
import BottomNavBar from '../components/BottomNavBar';
import '../App.css';

const SuperadminOrderDetail = () => {
  const navigate = useNavigate();
  const { orderId } = useParams();
  const [activeNav, setActiveNav] = useState('profile');
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isStatusDropdownOpen, setIsStatusDropdownOpen] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // All available order statuses
  const availableStatuses = [
    { id: 'new', label: 'Новый' },
    { id: 'paid', label: 'Оплачен' },
    { id: 'accepted', label: 'Принят' },
    { id: 'assembled', label: 'Собран' },
    { id: 'in_delivery', label: 'В доставке' },
    { id: 'delivered', label: 'Доставлен' },
    { id: 'cancelled', label: 'Отменен' }
  ];

  // Fetch order details
  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        setLoading(true);
        const data = await orderAPI.getDetail(orderId);
        setOrderData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch order details:', err);
        setError(err.message || 'Не удалось загрузить детали заказа');
      } finally {
        setLoading(false);
      }
    };

    fetchOrderDetails();
  }, [orderId]);

  // Handle status change
  const handleStatusChange = async (newStatus) => {
    if (!orderData || isUpdatingStatus) return;

    try {
      setIsUpdatingStatus(true);

      // Call API to update status
      await orderAPI.updateStatus(orderId, newStatus);

      // Update local state
      setOrderData({
        ...orderData,
        order: {
          ...orderData.order,
          status: newStatus
        }
      });

      // Close dropdown
      setIsStatusDropdownOpen(false);
    } catch (err) {
      console.error('Failed to update order status:', err);
      alert('Не удалось изменить статус заказа');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  // Format price in tenge
  const formatPrice = (price) => {
    return (price / 100).toLocaleString('ru-RU', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Не указана';
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

  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error || !orderData) {
    return (
      <div className="figma-container bg-white">
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            {error || 'Заказ не найден'}
          </div>
          <button
            onClick={() => navigate('/superadmin/orders')}
            className="bg-purple-primary text-white px-6 py-2 rounded-lg font-['Open_Sans'] text-sm"
          >
            Вернуться к списку
          </button>
        </div>
      </div>
    );
  }

  const { order, shop, items } = orderData;

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5 mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/superadmin/orders')}
            className="text-black text-xl"
          >
            ←
          </button>
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">Заказ #{order.id}</h1>
        </div>
      </div>

      {/* Status Section */}
      <div className="px-4 mb-6">
        <div className="bg-purple-light rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              Статус заказа
            </span>
            <span className={`px-3 py-1.5 rounded text-[12px] font-['Open_Sans'] font-normal uppercase tracking-wide ${getStatusColor(order.status)}`}>
              {getStatusLabel(order.status)}
            </span>
          </div>

          {/* Status Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsStatusDropdownOpen(!isStatusDropdownOpen)}
              disabled={isUpdatingStatus}
              className="w-full px-4 py-2 bg-white border border-gray-border rounded-lg text-[14px] font-['Open_Sans'] text-left flex items-center justify-between hover:bg-gray-50 disabled:opacity-50"
            >
              <span>{isUpdatingStatus ? 'Обновление...' : 'Изменить статус'}</span>
              <span className="text-gray-placeholder">{isStatusDropdownOpen ? '▲' : '▼'}</span>
            </button>

            {isStatusDropdownOpen && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-border rounded-lg shadow-lg overflow-hidden">
                {availableStatuses.map((status) => (
                  <button
                    key={status.id}
                    onClick={() => handleStatusChange(status.id)}
                    disabled={status.id === order.status}
                    className={`w-full px-4 py-2 text-[14px] font-['Open_Sans'] text-left hover:bg-purple-light transition-colors ${
                      status.id === order.status ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : ''
                    }`}
                  >
                    {status.label}
                    {status.id === order.status && ' (текущий)'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Customer Information */}
      <div className="px-4 mb-6">
        <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Информация о клиенте</h2>
        <div className="bg-white border border-gray-border rounded-lg p-4 space-y-3">
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Имя</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{order.customerName || 'Не указано'}</div>
          </div>
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Телефон</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{order.phone || 'Не указан'}</div>
          </div>
          {shop && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Магазин</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{shop.name} (ID: {shop.id})</div>
            </div>
          )}
        </div>
      </div>

      {/* Delivery Information */}
      <div className="px-4 mb-6">
        <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Доставка</h2>
        <div className="bg-white border border-gray-border rounded-lg p-4 space-y-3">
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Адрес</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{order.delivery_address || 'Не указан'}</div>
          </div>
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Дата доставки</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{formatDate(order.delivery_date)}</div>
          </div>
          {order.scheduled_time && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Время</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{order.scheduled_time}</div>
            </div>
          )}
        </div>
      </div>

      {/* Order Items */}
      <div className="px-4 mb-6">
        <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Товары</h2>
        <div className="space-y-2">
          {items && items.length > 0 ? (
            items.map((item) => (
              <div key={item.id} className="bg-white border border-gray-border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-[16px] font-['Open_Sans'] font-semibold text-black mb-1">
                      {item.product_name}
                    </div>
                    <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                      {formatPrice(item.product_price)} ₸ × {item.quantity} шт.
                    </div>
                  </div>
                  <div className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {formatPrice(item.item_total)} ₸
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-gray-placeholder text-center py-4">Товары не найдены</div>
          )}
        </div>
      </div>

      {/* Order Summary */}
      <div className="px-4 mb-6">
        <div className="bg-purple-light rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Подытог</span>
            <span className="text-[16px] font-['Open_Sans'] text-black">{formatPrice(order.subtotal || 0)} ₸</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">Доставка</span>
            <span className="text-[16px] font-['Open_Sans'] text-black">{formatPrice(order.delivery_cost || 0)} ₸</span>
          </div>
          <div className="border-t border-gray-border my-2"></div>
          <div className="flex items-center justify-between">
            <span className="text-[18px] font-['Open_Sans'] font-bold text-black">Итого</span>
            <span className="text-[18px] font-['Open_Sans'] font-bold text-black">{formatPrice(order.total || 0)} ₸</span>
          </div>
        </div>
      </div>

      {/* Notes */}
      {order.notes && (
        <div className="px-4 mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Комментарий</h2>
          <div className="bg-white border border-gray-border rounded-lg p-4">
            <div className="text-[14px] font-['Open_Sans'] text-black">{order.notes}</div>
          </div>
        </div>
      )}

      {/* Created Date */}
      <div className="px-4 mb-6">
        <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">
          Создан: {formatDate(order.created_at)}
        </div>
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

export default SuperadminOrderDetail;
