import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import { paymentAPI, formatPaymentLogForDisplay } from './services/paymentAPI';
import './App.css';

const PaymentLogs = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('');
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    shop_id: '',
    operation_type: '',
    limit: 50
  });
  const [autoRefresh, setAutoRefresh] = useState(false);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch logs
  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {
        ...filters,
        shop_id: filters.shop_id ? parseInt(filters.shop_id) : undefined
      };
      const data = await paymentAPI.getLogs(params);
      const formatted = data.map(formatPaymentLogForDisplay);
      setLogs(formatted);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      setError(err.message || 'Не удалось загрузить логи');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchLogs();
  }, [filters]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchLogs();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, filters]);

  const getStatusBadge = (log) => {
    const colors = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800'
    };

    const color = colors[log.status] || 'bg-gray-100 text-gray-800';

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${color}`}>
        {log.status}
      </span>
    );
  };

  if (loading && logs.length === 0) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-gray-400">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white pb-20">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-semibold mb-2">Audit Log платежей</h1>
              <p className="text-gray-600 text-sm">
                История операций payment-service
              </p>
            </div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={e => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Auto-refresh (5s)</span>
            </label>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Filters */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Shop ID
              </label>
              <input
                type="number"
                value={filters.shop_id}
                onChange={e => setFilters({...filters, shop_id: e.target.value})}
                placeholder="Все"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Операция
              </label>
              <select
                value={filters.operation_type}
                onChange={e => setFilters({...filters, operation_type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Все</option>
                <option value="create">Создание</option>
                <option value="status">Проверка статуса</option>
                <option value="refund">Возврат</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Лимит
              </label>
              <select
                value={filters.limit}
                onChange={e => setFilters({...filters, limit: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
              </select>
            </div>
          </div>
        </div>

        {/* Logs table */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Время</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Shop</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">БИН</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Операция</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">External ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Сумма</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Статус</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Ошибка</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                      Нет записей
                    </td>
                  </tr>
                ) : (
                  logs.map((log, index) => (
                    <tr key={log.id || index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-xs text-gray-600">{log.timestamp}</td>
                      <td className="px-4 py-3 text-sm">{log.shop_id}</td>
                      <td className="px-4 py-3 text-xs font-mono">{log.organization_bin}</td>
                      <td className="px-4 py-3 text-sm">{log.operationText}</td>
                      <td className="px-4 py-3 text-xs font-mono text-gray-600">
                        {log.external_id || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm">{log.amountTenge}</td>
                      <td className="px-4 py-3">{getStatusBadge(log)}</td>
                      <td className="px-4 py-3 text-xs text-red-600">
                        {log.error_message ? (
                          <span title={log.error_message}>
                            {log.error_message.substring(0, 30)}...
                          </span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-4 text-sm text-gray-600">
          Показано: {logs.length} записей
        </div>
      </div>

      <BottomNavBar activeNav={activeNav} onNavChange={handleNavChange} />
    </div>
  );
};

export default PaymentLogs;
