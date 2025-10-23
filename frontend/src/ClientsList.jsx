import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import { clientsAPI, formatClientForDisplay } from './services';
import './App.css';

const ClientsList = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('clients');
  const [searchQuery, setSearchQuery] = useState('');
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

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
        // Check if it's an auth error
        const isAuthMsg = err.message?.includes('Сессия истекла') ||
                          err.message?.includes('Необходима авторизация') ||
                          err.message?.includes('Недостаточно прав');
        setIsAuthError(isAuthMsg);
        setError(err.message || 'Не удалось загрузить клиентов');
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
      {/* Header with SearchToggle */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Клиенты</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle Icon */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск по имени или телефону"
            enabled={clients.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
          {/* Add Client Button */}
          <button
            onClick={() => navigate('/clients/add')}
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
          placeholder="Поиск по имени или телефону"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка клиентов...</div>
        </div>
      )}

      {/* Auth error - friendly prompt */}
      {error && isAuthError && (
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            Войдите в систему, чтобы увидеть клиентов
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
      {!loading && !error && filteredClients.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Клиенты не найдены' : 'Клиентов пока нет'}
          </div>
        </div>
      )}

      {/* Clients List */}
      <div className="mt-6">
        {!loading && !error && filteredClients.map((client, index) => (
          <div key={client.phone}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Client Item */}
            <div
              className="px-4 py-4 cursor-pointer hover:bg-gray-50"
              onClick={() => navigate(`/clients/${client.id}`)}
            >
              <div className="flex items-start justify-between">
                {/* Client Info */}
                <div className="flex-1">
                  {/* Client Name */}
                  <div className="mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {client.customerName}
                    </h3>
                  </div>

                  {/* Phone Number */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    {client.phone}
                  </p>

                  {/* Customer Since */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    Клиент с {client.customer_since}
                  </p>


                </div>

                {/* Total Spent */}
                <div className="text-right ml-4">
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {client.total_spent}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {!loading && !error && filteredClients.length > 0 && (
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

export default ClientsList;