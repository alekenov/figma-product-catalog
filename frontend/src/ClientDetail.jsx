import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import { clientsAPI, formatOrderForDisplay } from './services';
import './App.css';

const ClientDetail = () => {
  const navigate = useNavigate();
  const { clientId } = useParams();
  const [activeNav, setActiveNav] = useState('clients');
  const [client, setClient] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notesText, setNotesText] = useState('');
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedPhone, setEditedPhone] = useState('');

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch client details from API
  useEffect(() => {
    const fetchClientDetail = async () => {
      try {
        setLoading(true);
        const clientData = await clientsAPI.getClient(clientId);

        // Format client data
        const formattedClient = {
          ...clientData,
          total_spent: `${Math.floor(clientData.total_spent / 100).toLocaleString()} ₸`,
          average_order: `${Math.floor(clientData.average_order / 100).toLocaleString()} ₸`,
        };

        // Format orders data
        const formattedOrders = (clientData.orders || []).map(formatOrderForDisplay);

        setClient(formattedClient);
        setOrders(formattedOrders);
        setNotesText(clientData.notes || '');
        setError(null);
      } catch (err) {
        console.error('Failed to fetch client details:', err);
        setError('Не удалось загрузить данные клиента');
      } finally {
        setLoading(false);
      }
    };

    if (clientId) {
      fetchClientDetail();
    }
  }, [clientId]);

  const getStatusColor = (status) => {
    switch (status) {
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

  const handleSaveNotes = async () => {
    try {
      await clientsAPI.updateClientNotes(clientId, notesText);
      setIsEditingNotes(false);
      console.log('Notes saved successfully');
    } catch (err) {
      console.error('Failed to save notes:', err);
      // TODO: Show error message to user
    }
  };

  const handleSaveClientInfo = async () => {
    try {
      const updatedData = await clientsAPI.updateClient(clientId, {
        customerName: editedName,
        phone: editedPhone
      });

      // Update client state with new values
      setClient(prev => ({
        ...prev,
        customerName: updatedData.customerName,
        phone: updatedData.phone
      }));

      setIsEditingInfo(false);
      console.log('Client info saved successfully');
    } catch (err) {
      console.error('Failed to save client info:', err);
      // TODO: Show error message to user
      alert('Не удалось сохранить данные клиента: ' + (err.message || 'Неизвестная ошибка'));
    }
  };

  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Загрузка клиента...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center h-64">
          <div className="text-red-500">{error}</div>
        </div>
      </div>
    );
  }

  if (!client) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Клиент не найден</div>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header with back button */}
      <div className="flex items-center justify-between px-4 mt-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/clients')}
            className="w-6 h-6 flex items-center justify-center"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">Клиент</h1>
        </div>
      </div>

      {/* Client Information Section */}
      <div className="px-4 mt-6">
        {/* Client Name and Phone */}
        <div className="mb-6">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              {isEditingInfo ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      Имя клиента
                    </label>
                    <input
                      type="text"
                      value={editedName}
                      onChange={(e) => setEditedName(e.target.value)}
                      placeholder="Введите имя клиента"
                      className="w-full p-3 border border-gray-border rounded-lg text-[16px] font-['Open_Sans'] focus:outline-none focus:border-purple-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      Номер телефона
                    </label>
                    <input
                      type="tel"
                      value={editedPhone}
                      onChange={(e) => setEditedPhone(e.target.value)}
                      placeholder="+7 XXX XXX XX XX"
                      className="w-full p-3 border border-gray-border rounded-lg text-[16px] font-['Open_Sans'] focus:outline-none focus:border-purple-primary"
                    />
                  </div>
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={handleSaveClientInfo}
                      className="px-4 py-2 bg-purple-primary text-white text-[14px] font-['Open_Sans'] rounded-lg"
                    >
                      Сохранить
                    </button>
                    <button
                      onClick={() => {
                        setIsEditingInfo(false);
                        setEditedName(client.customerName);
                        setEditedPhone(client.phone);
                      }}
                      className="px-4 py-2 bg-gray-neutral text-black text-[14px] font-['Open_Sans'] rounded-lg"
                    >
                      Отмена
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <h2 className="text-[20px] font-['Open_Sans'] font-bold text-black mb-2">
                    {client.customerName}
                  </h2>
                  <p className="text-[16px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    {client.phone}
                  </p>
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    Клиент с {client.customer_since}
                  </p>
                </div>
              )}
            </div>
            {!isEditingInfo && (
              <button
                onClick={() => {
                  setEditedName(client.customerName);
                  setEditedPhone(client.phone);
                  setIsEditingInfo(true);
                }}
                className="text-purple-primary text-[14px] font-['Open_Sans'] ml-4"
              >
                Редактировать
              </button>
            )}
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-input rounded-lg p-4">
            <div className="text-[24px] font-['Open_Sans'] font-bold text-black">
              {client.total_orders}
            </div>
            <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              заказов
            </div>
          </div>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="text-[24px] font-['Open_Sans'] font-bold text-black">
              {client.total_spent}
            </div>
            <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              потрачено
            </div>
          </div>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="text-[24px] font-['Open_Sans'] font-bold text-black">
              {client.average_order}
            </div>
            <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              средний чек
            </div>
          </div>

          <div className="bg-gray-input rounded-lg p-4">
            <div className="text-[24px] font-['Open_Sans'] font-bold text-black">
              {orders.filter(order => order.status === 'delivered').length}
            </div>
            <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              завершено
            </div>
          </div>
        </div>

        {/* Notes Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
              Заметки о клиенте
            </h3>
            {!isEditingNotes && (
              <button
                onClick={() => setIsEditingNotes(true)}
                className="text-purple-primary text-[14px] font-['Open_Sans']"
              >
                Редактировать
              </button>
            )}
          </div>

          {isEditingNotes ? (
            <div>
              <textarea
                value={notesText}
                onChange={(e) => setNotesText(e.target.value)}
                placeholder="Добавить заметку о клиенте..."
                className="w-full h-24 p-3 border border-gray-border rounded-lg text-[14px] font-['Open_Sans'] resize-none focus:outline-none focus:border-purple-primary"
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={handleSaveNotes}
                  className="px-4 py-2 bg-purple-primary text-white text-[14px] font-['Open_Sans'] rounded-lg"
                >
                  Сохранить
                </button>
                <button
                  onClick={() => {
                    setIsEditingNotes(false);
                    setNotesText(client.notes || '');
                  }}
                  className="px-4 py-2 bg-gray-neutral text-black text-[14px] font-['Open_Sans'] rounded-lg"
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-gray-input rounded-lg p-3 min-h-[60px] flex items-start">
              {notesText ? (
                <p className="text-[14px] font-['Open_Sans'] text-black">
                  {notesText}
                </p>
              ) : (
                <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                  Нет заметок о клиенте
                </p>
              )}
            </div>
          )}
        </div>

        {/* Orders History Header */}
        <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black mb-4">
          История заказов ({orders.length})
        </h3>
      </div>

      {/* Orders List */}
      <div className="mt-2">
        {orders.length === 0 ? (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-placeholder">У клиента пока нет заказов</div>
          </div>
        ) : (
          orders.map((order, index) => (
            <div key={order.id}>
              {/* Divider */}
              <div className="border-t border-[#E0E0E0]"></div>

              {/* Order Item */}
              <div
                className="px-4 py-4 cursor-pointer hover:bg-gray-50"
                onClick={() => navigate(`/orders/${order.id}`)}
              >
                <div className="flex items-start justify-between">
                  {/* Order Info */}
                  <div className="flex-1">
                    {/* Order Number and Status */}
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                        {order.orderNumber}
                      </h4>
                      <span className={`px-[6px] py-[3px] rounded-[21px] text-[12px] font-['Open_Sans'] font-normal uppercase tracking-[1.2px] ${getStatusColor(order.status)}`}>
                        {order.statusLabel}
                      </span>
                    </div>

                    {/* Date */}
                    <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                      {order.date} в {order.time}
                    </p>

                    {/* Items count */}
                    <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                      {order.items.length} поз.
                    </p>
                  </div>

                  {/* Order Total */}
                  <div className="text-right ml-4">
                    <p className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {order.total}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}

        {/* Final divider */}
        {orders.length > 0 && (
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

export default ClientDetail;