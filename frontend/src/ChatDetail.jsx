import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { chatsAPI } from './services/api';
import './App.css';

const ChatDetail = () => {
  const navigate = useNavigate();
  const { chatId } = useParams();
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);

  const handleBack = () => {
    navigate('/superadmin/chats');
  };

  // Fetch chat from API
  useEffect(() => {
    const fetchChat = async () => {
      if (!chatId) {
        setError('Не указан ID чата');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const chatData = await chatsAPI.getChatDetail(chatId);
        setChat(chatData);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch chat:', err);
        const isAuthMsg = err.message?.includes('Сессия истекла') ||
                          err.message?.includes('Необходима авторизация') ||
                          err.message?.includes('Недостаточно прав');
        setIsAuthError(isAuthMsg);
        setError(err.message || 'Не удалось загрузить чат');
      } finally {
        setLoading(false);
      }
    };

    fetchChat();
  }, [chatId]);

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

  // Loading state
  if (loading) {
    return (
      <div className="figma-container bg-white min-h-screen">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Загрузка чата...</div>
        </div>
      </div>
    );
  }

  // Auth error
  if (error && isAuthError) {
    return (
      <div className="figma-container bg-white min-h-screen">
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
      </div>
    );
  }

  // Other errors
  if (error) {
    return (
      <div className="figma-container bg-white min-h-screen">
        <div className="flex flex-col justify-center items-center h-64">
          <div className="text-red-500 mb-4">{error}</div>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-purple-primary text-white rounded"
          >
            Назад к чатам
          </button>
        </div>
      </div>
    );
  }

  // No data
  if (!chat) {
    return (
      <div className="figma-container bg-white min-h-screen">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-placeholder">Чат не найден</div>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white min-h-screen">
      {/* Header */}
      <div className="bg-white h-[62px] relative">
        <div className="border-b border-gray-border"></div>

        {/* Back button */}
        <button
          onClick={handleBack}
          className="absolute left-4 top-[19px] w-6 h-6 flex items-center justify-center"
        >
          <svg className="w-6 h-6 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Chat title */}
        <h1 className="absolute left-12 top-4 text-xl font-['Open_Sans'] font-normal leading-[30px]">
          Чат #{chat.id}
        </h1>

        {/* Channel badge */}
        <div className="absolute right-4 top-[18px]">
          <span className={`px-[6px] py-[3px] rounded-[21px] text-[12px] font-['Open_Sans'] font-normal uppercase tracking-[1.2px] ${getChannelColor(chat.channel)}`}>
            {chat.channel}
          </span>
        </div>
      </div>

      {/* Chat Info Section */}
      <div className="px-4 py-4 bg-purple-light">
        <div className="space-y-2">
          {/* Customer Name */}
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Клиент</div>
            <div className="text-[16px] font-['Open_Sans'] font-bold text-black">
              {chat.customer_name || `Пользователь ${chat.user_id.substring(0, 8)}`}
            </div>
          </div>

          {/* Phone if available */}
          {chat.customer_phone && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Телефон</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{chat.customer_phone}</div>
            </div>
          )}

          {/* Chat Stats */}
          <div className="grid grid-cols-3 gap-3 mt-4">
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Сообщений</div>
              <div className="text-[16px] font-['Open_Sans'] font-bold text-black">{chat.message_count}</div>
            </div>
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Стоимость</div>
              <div className="text-[16px] font-['Open_Sans'] font-bold text-black">
                ${Number(chat.total_cost_usd).toFixed(3)}
              </div>
            </div>
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Заказ</div>
              <div className="text-[16px] font-['Open_Sans'] font-bold text-black">
                {chat.created_order ? (
                  <span className="text-green-success">Да</span>
                ) : (
                  <span className="text-gray-400">Нет</span>
                )}
              </div>
            </div>
          </div>

          {/* Order link if exists */}
          {chat.order_id && (
            <div className="mt-3">
              <button
                onClick={() => navigate(`/orders/${chat.order_id}`)}
                className="px-4 py-2 bg-purple-primary text-white text-[14px] font-['Open_Sans'] rounded hover:bg-purple-600 transition-colors"
              >
                Перейти к заказу #{chat.order_id}
              </button>
            </div>
          )}

          {/* Session timing */}
          <div className="mt-3 pt-3 border-t border-gray-border">
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Начало: {formatDate(chat.started_at)}</div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder">Последнее: {formatDate(chat.last_message_at)}</div>
          </div>
        </div>
      </div>

      {/* Messages Section */}
      <div className="px-4 py-6">
        <h2 className="text-[20px] font-['Open_Sans'] font-bold text-black mb-4">Сообщения</h2>

        {chat.messages && chat.messages.length > 0 ? (
          <div className="space-y-4">
            {chat.messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-purple-primary text-white'
                    : 'bg-gray-100 text-black'
                }`}>
                  {/* Role badge */}
                  <div className={`text-[10px] font-['Open_Sans'] uppercase tracking-[1px] mb-1 ${
                    message.role === 'user' ? 'text-purple-200' : 'text-gray-500'
                  }`}>
                    {message.role === 'user' ? 'Клиент' : 'AI Агент'}
                  </div>

                  {/* Message content */}
                  <div className="text-[14px] font-['Open_Sans'] leading-normal whitespace-pre-wrap">
                    {message.content}
                  </div>

                  {/* Message metadata */}
                  <div className={`text-[10px] font-['Open_Sans'] mt-2 flex items-center gap-2 ${
                    message.role === 'user' ? 'text-purple-200' : 'text-gray-400'
                  }`}>
                    <span>{new Date(message.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</span>
                    {Number(message.cost_usd) > 0 && (
                      <>
                        <span>•</span>
                        <span>${Number(message.cost_usd).toFixed(4)}</span>
                      </>
                    )}
                  </div>

                  {/* Tools/Metadata if present */}
                  {message.message_metadata && Object.keys(message.message_metadata).length > 0 && (
                    <div className={`text-[10px] font-['Open_Sans'] mt-2 pt-2 border-t ${
                      message.role === 'user' ? 'border-purple-400' : 'border-gray-300'
                    }`}>
                      {message.message_metadata.tools_used && (
                        <div className={message.role === 'user' ? 'text-purple-200' : 'text-gray-500'}>
                          Использованы инструменты: {message.message_metadata.tools_used.join(', ')}
                        </div>
                      )}
                      {message.message_metadata.tokens && (
                        <div className={message.role === 'user' ? 'text-purple-200' : 'text-gray-500'}>
                          Токенов: {message.message_metadata.tokens}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-gray-placeholder">Нет сообщений</div>
          </div>
        )}
      </div>

      {/* Bottom spacing */}
      <div className="h-8" />
    </div>
  );
};

export default ChatDetail;
