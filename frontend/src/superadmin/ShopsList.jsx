import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { shopAPI } from '../api/superadmin';
import SuperadminLayout from './SuperadminLayout';

/**
 * Shops List Component
 * Shows all shops with ability to block/unblock and view details
 */
const ShopsList = () => {
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterActive, setFilterActive] = useState(null); // null = all, true = active, false = blocked

  useEffect(() => {
    loadShops();
  }, [filterActive]);

  const loadShops = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterActive !== null) {
        params.is_active = filterActive;
      }
      const data = await shopAPI.list(params);
      setShops(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Ошибка загрузки магазинов');
      console.error('Failed to load shops:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (shop) => {
    try {
      if (shop.is_active) {
        await shopAPI.block(shop.id);
      } else {
        await shopAPI.unblock(shop.id);
      }
      // Reload shops to get updated status
      await loadShops();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
        Активен
      </span>
    ) : (
      <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
        Заблокирован
      </span>
    );
  };

  return (
    <SuperadminLayout>
      <div>
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Магазины</h2>

          {/* Filter buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilterActive(null)}
              className={`px-4 py-2 rounded-md text-sm ${
                filterActive === null
                  ? 'bg-purple-primary text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setFilterActive(true)}
              className={`px-4 py-2 rounded-md text-sm ${
                filterActive === true
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Активные
            </button>
            <button
              onClick={() => setFilterActive(false)}
              className={`px-4 py-2 rounded-md text-sm ${
                filterActive === false
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Заблокированные
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Загрузка...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        ) : shops.length === 0 ? (
          <div className="bg-gray-50 rounded-md p-8 text-center">
            <p className="text-gray-500">Магазины не найдены</p>
          </div>
        ) : (
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Название
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Город
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Телефон
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дата создания
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {shops.map((shop) => (
                  <tr key={shop.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {shop.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {shop.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {shop.city || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {shop.phone || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(shop.is_active)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(shop.created_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <Link
                          to={`/superadmin/shops/${shop.id}`}
                          className="text-purple-primary hover:text-purple-700"
                        >
                          Детали
                        </Link>
                        <button
                          onClick={() => handleToggleActive(shop)}
                          className={`${
                            shop.is_active
                              ? 'text-red-600 hover:text-red-900'
                              : 'text-green-600 hover:text-green-900'
                          }`}
                        >
                          {shop.is_active ? 'Заблокировать' : 'Разблокировать'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </SuperadminLayout>
  );
};

export default ShopsList;
