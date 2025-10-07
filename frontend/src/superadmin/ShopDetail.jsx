import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { shopAPI, userAPI } from '../api/superadmin';
import BottomNavBar from '../components/BottomNavBar';
import '../App.css';

const ShopDetail = () => {
  const { shopId } = useParams();
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile');
  const [shop, setShop] = useState(null);
  const [owner, setOwner] = useState(null);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  useEffect(() => {
    loadShopDetail();
  }, [shopId]);

  const loadShopDetail = async () => {
    try {
      setLoading(true);
      const data = await shopAPI.getDetail(shopId);
      setShop(data.shop);
      setOwner(data.owner);
      setUsers(data.users || []);
      setStats(data.stats);
      setError(null);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки данных');
      console.error('Failed to load shop detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleShop = async () => {
    try {
      if (shop.is_active) {
        await shopAPI.block(shop.id);
      } else {
        await shopAPI.unblock(shop.id);
      }
      await loadShopDetail();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  const handleToggleUser = async (user) => {
    try {
      if (user.is_active) {
        await userAPI.block(user.id);
      } else {
        await userAPI.unblock(user.id);
      }
      await loadShopDetail();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  const handleResetPassword = async (user) => {
    const newPassword = prompt(`Введите новый пароль для ${user.name}:`);
    if (!newPassword || newPassword.length < 6) {
      alert('Пароль должен быть не менее 6 символов');
      return;
    }

    try {
      await userAPI.resetPassword(user.id, newPassword);
      alert('Пароль успешно сброшен');
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
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

  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error || !shop) {
    return (
      <div className="figma-container bg-white">
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            {error || 'Магазин не найден'}
          </div>
          <button
            onClick={() => navigate('/superadmin/shops')}
            className="bg-purple-primary text-white px-6 py-2 rounded-lg font-['Open_Sans'] text-sm"
          >
            Вернуться к списку
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5 mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/superadmin/shops')}
            className="text-black text-xl"
          >
            ←
          </button>
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">{shop.name}</h1>
        </div>
      </div>

      {/* Shop Status Section */}
      <div className="px-4 mb-6">
        <div className="bg-purple-light rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
              Статус магазина
            </span>
            <span className={`px-3 py-1.5 rounded text-[12px] font-['Open_Sans'] font-normal uppercase tracking-wide ${
              shop.is_active
                ? 'bg-green-success text-white'
                : 'bg-gray-400 text-white'
            }`}>
              {shop.is_active ? 'Активен' : 'Заблокирован'}
            </span>
          </div>

          <button
            onClick={handleToggleShop}
            className={`w-full px-4 py-2 rounded-lg text-[14px] font-['Open_Sans'] text-white ${
              shop.is_active
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-green-success hover:bg-green-600'
            }`}
          >
            {shop.is_active ? 'Заблокировать магазин' : 'Разблокировать магазин'}
          </button>
        </div>
      </div>

      {/* Shop Information */}
      <div className="px-4 mb-6">
        <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Информация о магазине</h2>
        <div className="bg-white border border-gray-border rounded-lg p-4 space-y-3">
          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">ID</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{shop.id}</div>
          </div>

          {shop.address && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Адрес</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{shop.address}</div>
            </div>
          )}

          {shop.city && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Город</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{shop.city}</div>
            </div>
          )}

          {shop.phone && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Телефон</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">{shop.phone}</div>
            </div>
          )}

          {owner && (
            <div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Владелец</div>
              <div className="text-[16px] font-['Open_Sans'] text-black">
                {owner.name} ({owner.phone})
              </div>
            </div>
          )}

          <div>
            <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mb-1">Дата создания</div>
            <div className="text-[16px] font-['Open_Sans'] text-black">{formatDate(shop.created_at)}</div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="px-4 mb-6">
          <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Статистика</h2>
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-purple-light rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-purple-primary">
                {stats.products_count || 0}
              </div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Товары
              </div>
            </div>
            <div className="bg-purple-light rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-green-success">
                {stats.orders_count || 0}
              </div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Заказы
              </div>
            </div>
            <div className="bg-purple-light rounded-lg p-3 text-center">
              <div className="text-[24px] font-['Open_Sans'] font-bold text-status-blue">
                {stats.users_count || 0}
              </div>
              <div className="text-[12px] font-['Open_Sans'] text-gray-placeholder mt-1">
                Пользователи
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Users Section */}
      <div className="px-4 mb-6">
        <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-3">Пользователи</h2>

        {users.length === 0 ? (
          <div className="text-gray-placeholder text-center py-4">Нет пользователей</div>
        ) : (
          <div className="space-y-2">
            {users.map((user) => (
              <div key={user.id} className="bg-white border border-gray-border rounded-lg p-4">
                {/* User Info */}
                <div className="mb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-[16px] font-['Open_Sans'] font-semibold text-black">
                      {user.name}
                    </h3>
                    {user.is_superadmin && (
                      <span className="px-2 py-0.5 text-[10px] rounded-full bg-yellow-100 text-yellow-800 font-normal">
                        Superadmin
                      </span>
                    )}
                  </div>

                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    {user.phone}
                  </p>

                  <div className="flex items-center gap-2">
                    <span className="text-[13px] font-['Open_Sans'] text-gray-placeholder">
                      Роль: {user.role}
                    </span>
                    <span className={`px-2 py-0.5 text-[11px] rounded ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Активен' : 'Заблокирован'}
                    </span>
                  </div>
                </div>

                {/* User Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleResetPassword(user)}
                    className="flex-1 px-3 py-1.5 bg-purple-primary text-white rounded-lg text-[13px] font-['Open_Sans'] font-normal"
                  >
                    Сбросить пароль
                  </button>

                  {!user.is_superadmin && (
                    <button
                      onClick={() => handleToggleUser(user)}
                      className={`flex-1 px-3 py-1.5 rounded-lg text-[13px] font-['Open_Sans'] font-normal text-white ${
                        user.is_active ? 'bg-red-500' : 'bg-green-success'
                      }`}
                    >
                      {user.is_active ? 'Заблокировать' : 'Разблокировать'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
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

export default ShopDetail;
