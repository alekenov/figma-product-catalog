import React, { useState, useEffect } from 'react';
import { statsAPI } from '../api/superadmin';
import SuperadminLayout from './SuperadminLayout';

/**
 * Superadmin Statistics Component
 * Shows platform-wide statistics
 */
const SuperadminStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await statsAPI.getPlatformStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки статистики');
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
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
        </div>
      </SuperadminLayout>
    );
  }

  return (
    <SuperadminLayout>
      <div>
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Статистика платформы</h2>
          <button
            onClick={loadStats}
            className="px-4 py-2 bg-purple-primary text-white rounded-md hover:bg-purple-700 text-sm"
          >
            Обновить
          </button>
        </div>

        {/* Shops Statistics */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Магазины</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-purple-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Всего</p>
              <p className="text-3xl font-bold text-purple-primary">{stats.shops.total}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Активные</p>
              <p className="text-3xl font-bold text-green-600">{stats.shops.active}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Заблокированные</p>
              <p className="text-3xl font-bold text-red-600">{stats.shops.blocked}</p>
            </div>
          </div>
        </div>

        {/* Users Statistics */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Пользователи</h3>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Всего</p>
              <p className="text-3xl font-bold text-blue-600">{stats.users.total}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Активные</p>
              <p className="text-3xl font-bold text-green-600">{stats.users.active}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-md">
              <p className="text-sm text-gray-500">Заблокированные</p>
              <p className="text-3xl font-bold text-red-600">{stats.users.blocked}</p>
            </div>
          </div>

          {/* Users by Role */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">По ролям:</p>
            <div className="grid grid-cols-4 gap-4">
              {Object.entries(stats.users.by_role).map(([role, count]) => (
                <div key={role} className="bg-gray-50 p-3 rounded-md">
                  <p className="text-xs text-gray-500 uppercase">{role}</p>
                  <p className="text-xl font-bold text-gray-900">{count}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Orders Statistics */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Заказы</h3>
          <div className="bg-indigo-50 p-4 rounded-md">
            <p className="text-sm text-gray-500">Всего заказов</p>
            <p className="text-3xl font-bold text-indigo-600">{stats.orders.total}</p>
          </div>
        </div>

        {/* Products Statistics */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Товары</h3>
          <div className="bg-pink-50 p-4 rounded-md">
            <p className="text-sm text-gray-500">Всего товаров</p>
            <p className="text-3xl font-bold text-pink-600">{stats.products.total}</p>
          </div>
        </div>

        {/* Timestamp */}
        <div className="text-center text-sm text-gray-500">
          Обновлено: {new Date(stats.timestamp).toLocaleString('ru-RU')}
        </div>
      </div>
    </SuperadminLayout>
  );
};

export default SuperadminStats;
