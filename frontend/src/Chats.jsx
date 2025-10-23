import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import { chatsAPI } from './services';
import './App.css';

const Chats = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('chats');
  const [channelFilter, setChannelFilter] = useState('all');
  const [hasOrderFilter, setHasOrderFilter] = useState(null); // null, true, false
  const [searchQuery, setSearchQuery] = useState('');
  const [chats, setChats] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch chats from API
  useEffect(() => {
    const fetchChats = async () => {
      try {
        setLoading(true);
        const params = {
          limit: 50,
          ...(channelFilter !== 'all' && { channel: channelFilter }),
          ...(hasOrderFilter !== null && { has_order: hasOrderFilter }),
          ...(searchQuery && { search: searchQuery })
        };
        const chatSessions = await chatsAPI.getChats(params);
        setChats(chatSessions);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch chats:', err);
        const isAuthMsg = err.message?.includes('Сессия истекла') ||
                          err.message?.includes('Необходима авторизация') ||
                          err.message?.includes('Недостаточно прав');
        setIsAuthError(isAuthMsg);
        setError(err.message || 'Не удалось загрузить чаты');
      } finally {
        setLoading(false);
      }
    };

    fetchChats();
  }, [channelFilter, hasOrderFilter, searchQuery]);

  // Fetch statistics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await chatsAPI.getStats();
        setStats(statsData);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      }
    };

    fetchStats();
  }, []);

  const channelFilters = [
    { id: 'all', label: 'Все' },
    { id: 'telegram', label: 'Telegram' },
    { id: 'whatsapp', label: 'WhatsApp' },
    { id: 'web', label: 'Web' }
  ];

  const orderFilters = [
    { id: null, label: 'Все' },
    { id: true, label: 'С заказом' },
    { id: false, label: 'Без заказа' }
  ];

  // Channel badge colors
  const getChannelColor = (channel) => {
    switch (channel) {
      case 'telegram':
        return 'bg-blue-500 text-white';
      case 'whatsapp':
        return 'bg-green-500 text-white';
      case 'web':
        return 'bg-purple-500 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  // Format date
  const formatDate = (isoDateString) => {
    if (!isoDateString) return '';
    const date = new Date(isoDateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const timeStr = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

    if (date.toDateString() === today.toDateString()) {
      return `Сегодня, ${timeStr}`;
    }
    if (date.toDateString() === yesterday.toDateString()) {
      return `Вчера, ${timeStr}`;
    }

    const day = date.getDate();
    const month = date.toLocaleDateString('ru-RU', { month: 'short' });
    return `${day} ${month}, ${timeStr}`;
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

      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-[24px] font-['Open_Sans'] font-normal">Чаты</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск по чатам"
            enabled={chats.length > 0}
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
          placeholder="Поиск по имени или телефону"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="px-4 mt-6 grid grid-cols-2 gap-3">
          <div className="bg-purple-light p-3 rounded-lg">
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Сегодня</div>
            <div className="text-[20px] font-['Open_Sans'] font-bold text-black">{stats.total_chats_today}</div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">чатов</div>
          </div>
          <div className="bg-purple-light p-3 rounded-lg">
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Конверсия</div>
            <div className="text-[20px] font-['Open_Sans'] font-bold text-black">{stats.conversion_rate}%</div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">в заказы</div>
          </div>
          <div className="bg-purple-light p-3 rounded-lg">
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Средняя стоимость</div>
            <div className="text-[20px] font-['Open_Sans'] font-bold text-black">${Number(stats.avg_cost_usd).toFixed(3)}</div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">за чат</div>
          </div>
          <div className="bg-purple-light p-3 rounded-lg">
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Сообщений</div>
            <div className="text-[20px] font-['Open_Sans'] font-bold text-black">{stats.avg_messages_per_chat}</div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">в среднем</div>
          </div>
        </div>
      )}

      {/* Filter Pills - Channel and Order Status */}
      <div className="flex gap-2 px-4 mt-6 overflow-x-auto">
        {/* Channel Filters */}
        {channelFilters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setChannelFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[16px] font-['Open_Sans'] font-normal whitespace-nowrap ${
              channelFilter === filter.id
                ? 'bg-purple-primary text-white'
                : 'bg-purple-light text-black'
            }`}
          >
            {filter.label}
          </button>
        ))}

        {/* Divider */}
        <div className="w-px bg-gray-border mx-1" />

        {/* Order Filters */}
        {orderFilters.map((filter) => (
          <button
            key={filter.id === null ? 'all' : filter.id.toString()}
            onClick={() => setHasOrderFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[16px] font-['Open_Sans'] font-normal whitespace-nowrap ${
              hasOrderFilter === filter.id
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
          <div className="text-gray-placeholder">Загрузка чатов...</div>
        </div>
      )}

      {/* Auth error - friendly prompt */}
      {error && isAuthError && (
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            Войдите в систему, чтобы увидеть чаты
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
      {!loading && !error && chats.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Чаты не найдены' : 'Чатов пока нет'}
          </div>
        </div>
      )}

      {/* Chats List */}
      <div className="mt-6">
        {!loading && !error && chats.map((chat) => (
          <div key={chat.id}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Chat Item */}
            <div
              className="px-4 py-4 cursor-pointer hover:bg-gray-50"
              onClick={() => navigate(`/superadmin/chats/${chat.id}`)}
            >
              <div className="flex items-start justify-between">
                {/* Chat Info */}
                <div className="flex-1">
                  {/* Channel Badge and Customer Name */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-[6px] py-[3px] rounded-[21px] text-[12px] font-['Open_Sans'] font-normal uppercase tracking-[1.2px] ${getChannelColor(chat.channel)}`}>
                      {chat.channel}
                    </span>
                    {chat.created_order && (
                      <span className="px-[6px] py-[3px] bg-green-success rounded-[21px] text-[12px] font-['Open_Sans'] font-normal text-white uppercase tracking-[1.2px]">
                        Заказ
                      </span>
                    )}
                  </div>

                  {/* Customer Name or User ID */}
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black mb-1">
                    {chat.customer_name || `Пользователь ${chat.user_id.substring(0, 8)}`}
                  </p>

                  {/* Phone if available */}
                  {chat.customer_phone && (
                    <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      {chat.customer_phone}
                    </p>
                  )}

                  {/* Date */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    {formatDate(chat.last_message_at)}
                  </p>
                </div>

                {/* Chat Metrics */}
                <div className="text-right ml-4">
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                    {chat.message_count}
                  </p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    сообщ.
                  </p>
                  {Number(chat.total_cost_usd) > 0 && (
                    <p className="text-[12px] font-['Open_Sans'] text-gray-400">
                      ${Number(chat.total_cost_usd).toFixed(3)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {chats.length > 0 && <div className="border-t border-gray-border"></div>}
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

export default Chats;
