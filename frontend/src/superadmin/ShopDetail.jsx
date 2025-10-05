import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { shopAPI, userAPI } from '../api/superadmin';
import SuperadminLayout from './SuperadminLayout';

/**
 * Shop Detail Component
 * Shows shop details, users, and statistics
 */
const ShopDetail = () => {
  const { shopId } = useParams();
  const navigate = useNavigate();
  const [shop, setShop] = useState(null);
  const [owner, setOwner] = useState(null);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (loading) {
    return (
      <SuperadminLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Загрузка...</p>
        </div>
      </SuperadminLayout>
    );
  }

  if (error) {
    return (
      <SuperadminLayout>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={() => navigate('/superadmin')}
            className="mt-4 text-purple-primary hover:underline"
          >
            ← Назад к списку
          </button>
        </div>
      </SuperadminLayout>
    );
  }

  return (
    <SuperadminLayout>
      <div>
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/superadmin')}
            className="text-purple-primary hover:underline mb-4"
          >
            ← Назад к списку
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{shop.name}</h2>
              <p className="text-sm text-gray-500 mt-1">ID: {shop.id}</p>
            </div>
            <button
              onClick={handleToggleShop}
              className={`px-4 py-2 rounded-md text-white text-sm ${
                shop.is_active
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {shop.is_active ? 'Заблокировать магазин' : 'Разблокировать магазин'}
            </button>
          </div>
        </div>

        {/* Shop Info */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Информация о магазине</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Адрес</p>
              <p className="text-sm font-medium">{shop.address || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Город</p>
              <p className="text-sm font-medium">{shop.city || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Телефон</p>
              <p className="text-sm font-medium">{shop.phone || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Статус</p>
              <p className="text-sm font-medium">
                {shop.is_active ? (
                  <span className="text-green-600">Активен</span>
                ) : (
                  <span className="text-red-600">Заблокирован</span>
                )}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Владелец</p>
              <p className="text-sm font-medium">
                {owner ? `${owner.name} (${owner.phone})` : '-'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Дата создания</p>
              <p className="text-sm font-medium">
                {new Date(shop.created_at).toLocaleDateString('ru-RU')}
              </p>
            </div>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Статистика</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-purple-50 p-4 rounded-md">
                <p className="text-sm text-gray-500">Товары</p>
                <p className="text-2xl font-bold text-purple-primary">{stats.products_count}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-md">
                <p className="text-sm text-gray-500">Заказы</p>
                <p className="text-2xl font-bold text-green-600">{stats.orders_count}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-md">
                <p className="text-sm text-gray-500">Пользователи</p>
                <p className="text-2xl font-bold text-blue-600">{stats.users_count}</p>
              </div>
            </div>
          </div>
        )}

        {/* Users */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Пользователи</h3>
          </div>
          {users.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              Нет пользователей
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Имя
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Телефон
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Роль
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.phone}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.role}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_active ? (
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          Активен
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                          Заблокирован
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleResetPassword(user)}
                          className="text-purple-primary hover:text-purple-700"
                        >
                          Сбросить пароль
                        </button>
                        {!user.is_superadmin && (
                          <button
                            onClick={() => handleToggleUser(user)}
                            className={`${
                              user.is_active
                                ? 'text-red-600 hover:text-red-900'
                                : 'text-green-600 hover:text-green-900'
                            }`}
                          >
                            {user.is_active ? 'Заблокировать' : 'Разблокировать'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </SuperadminLayout>
  );
};

export default ShopDetail;
