import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import SearchInput from './components/SearchInput';
import { clientsAPI, formatClientForDisplay } from './services/api';
import './App.css';

const ClientsList = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('clients');
  const [searchQuery, setSearchQuery] = useState('');
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch clients from API
  useEffect(() => {
    const fetchClients = async () => {
      try {
        setLoading(true);
        const rawClients = await clientsAPI.getClients({ limit: 50 });
        const formattedClients = rawClients.map(formatClientForDisplay);
        setClients(formattedClients);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch clients:', err);
        setError('Не удалось загрузить клиентов');
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  // Apply search filter to clients
  const filteredClients = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return clients;
    }

    return clients.filter(client =>
      client.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      client.phone.includes(searchQuery)
    );
  }, [clients, searchQuery]);

  const getStatusColor = (lastOrderStatus) => {
    if (!lastOrderStatus) return 'bg-gray-100 text-gray-800';

    switch (lastOrderStatus) {
      case 'new':
        return 'bg-[#eb5757] text-white';
      case 'paid':
        return 'bg-[#5e81dc] text-white';
      case 'accepted':
        return 'bg-[#dc5ec0] text-white';
      case 'assembled':
        return 'bg-[#f8c20b] text-white';
      case 'in_delivery':
        return 'bg-[#7fc663] text-white';
      case 'delivered':
        return 'bg-[#34c759] text-white';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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

  return (
    <div className="figma-container bg-white">
      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-[24px] font-['Open_Sans'] font-normal">Клиенты</h1>
        <div className="flex items-center gap-4">
          {/* Search icon */}
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" strokeWidth="2"/>
            <path strokeWidth="2" strokeLinecap="round" d="M21 21l-4.35-4.35"/>
          </svg>
        </div>
      </div>

      {/* Search Input */}
      <SearchInput
        placeholder="Поиск по имени или телефону"
        value={searchQuery}
        onChange={setSearchQuery}
      />

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка клиентов...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex justify-center items-center py-8">
          <div className="text-red-500">{error}</div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredClients.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Клиенты не найдены' : 'Клиентов пока нет'}
          </div>
        </div>
      )}

      {/* Clients List */}
      <div className="mt-4">
        {!loading && !error && filteredClients.map((client, index) => (
          <div key={client.phone}>
            {/* Divider */}
            <div className="border-t border-[#E0E0E0]"></div>

            {/* Client Item */}
            <div
              className="px-4 py-4 cursor-pointer hover:bg-gray-50"
              onClick={() => navigate(`/client/${encodeURIComponent(client.phone)}`)}
            >
              <div className="flex items-start justify-between">
                {/* Client Info */}
                <div className="flex-1">
                  {/* Client Name and Phone */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {client.customerName}
                    </h3>
                    {client.last_order_status && (
                      <span className={`px-[6px] py-[3px] rounded-[21px] text-[12px] font-['Open_Sans'] font-normal uppercase tracking-[1.2px] ${getStatusColor(client.last_order_status)}`}>
                        {getStatusLabel(client.last_order_status)}
                      </span>
                    )}
                  </div>

                  {/* Phone Number */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    {client.phone}
                  </p>

                  {/* Customer Since */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    Клиент с {client.customer_since}
                  </p>

                  {/* Statistics Row */}
                  <div className="flex items-center gap-6 mt-2">
                    <div className="text-[14px] font-['Open_Sans'] text-black">
                      <span className="font-bold">{client.total_orders}</span> заказов
                    </div>
                    <div className="text-[14px] font-['Open_Sans'] text-black">
                      Средний: <span className="font-bold">{client.average_order}</span>
                    </div>
                  </div>

                  {/* Last Order Number if exists */}
                  {client.last_order_number && (
                    <p className="text-[12px] font-['Open_Sans'] text-gray-placeholder mt-1">
                      Последний заказ: {client.last_order_number}
                    </p>
                  )}
                </div>

                {/* Total Spent */}
                <div className="text-right ml-4">
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {client.total_spent}
                  </p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    всего
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {!loading && !error && filteredClients.length > 0 && (
          <div className="border-t border-[#E0E0E0]"></div>
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

export default ClientsList;