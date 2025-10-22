import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import { paymentAPI, formatPaymentConfigForDisplay } from './services/paymentAPI';
import './App.css';

const PaymentConfigs = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('');
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [formData, setFormData] = useState({
    shop_id: '',
    organization_bin: '',
    is_active: true,
    provider: 'kaspi',
    description: ''
  });
  const [testPayment, setTestPayment] = useState({
    shop_id: 8,
    phone: '77015211545',
    amount: 100,
    message: 'Тестовый платёж'
  });
  const [testResult, setTestResult] = useState(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch configs
  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const data = await paymentAPI.getConfigs();
      const formatted = data.map(formatPaymentConfigForDisplay);
      setConfigs(formatted);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch configs:', err);
      setError(err.message || 'Не удалось загрузить конфигурации');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConfig = () => {
    setEditingConfig(null);
    setFormData({
      shop_id: '',
      organization_bin: '',
      is_active: true,
      provider: 'kaspi',
      description: ''
    });
    setShowModal(true);
  };

  const handleEditConfig = (config) => {
    setEditingConfig(config);
    setFormData({
      shop_id: config.shop_id,
      organization_bin: config.organization_bin,
      is_active: config.is_active,
      provider: config.provider,
      description: config.description || ''
    });
    setShowModal(true);
  };

  const handleSaveConfig = async () => {
    try {
      if (editingConfig) {
        // Update existing
        await paymentAPI.updateConfig(editingConfig.id, {
          is_active: formData.is_active,
          description: formData.description
        });
      } else {
        // Create new
        await paymentAPI.createConfig({
          shop_id: parseInt(formData.shop_id),
          organization_bin: formData.organization_bin,
          is_active: formData.is_active,
          provider: formData.provider,
          description: formData.description
        });
      }

      setShowModal(false);
      fetchConfigs();
    } catch (err) {
      alert(`Ошибка: ${err.message}`);
    }
  };

  const handleDeleteConfig = async (id) => {
    if (!confirm('Удалить конфигурацию?')) return;

    try {
      await paymentAPI.deleteConfig(id);
      fetchConfigs();
    } catch (err) {
      alert(`Ошибка удаления: ${err.message}`);
    }
  };

  const handleTestPayment = async () => {
    try {
      setTestResult({ loading: true });
      const result = await paymentAPI.createTestPayment(testPayment);
      setTestResult({ success: true, data: result });
    } catch (err) {
      setTestResult({ success: false, error: err.message });
    }
  };

  const handleCheckStatus = async () => {
    if (!testResult?.data?.external_id) return;

    try {
      const status = await paymentAPI.checkPaymentStatus(testResult.data.external_id);
      setTestResult(prev => ({ ...prev, statusData: status }));
    } catch (err) {
      alert(`Ошибка проверки: ${err.message}`);
    }
  };

  if (loading) {
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
          <h1 className="text-2xl font-semibold mb-2">Конфигурации БИН</h1>
          <p className="text-gray-600 text-sm">
            Управление организациями для Kaspi Pay
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Create button */}
        <button
          onClick={handleCreateConfig}
          className="mb-4 px-4 py-2 bg-purple-primary text-white rounded-lg hover:bg-purple-700 transition"
        >
          + Добавить БИН
        </button>

        {/* Configs table */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden mb-6">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Shop ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">БИН</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Статус</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Описание</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {configs.map(config => (
                <tr key={config.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm">{config.shop_id}</td>
                  <td className="px-4 py-3 text-sm font-mono">{config.organization_bin}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={config.statusColor}>
                      {config.statusText}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{config.description || '-'}</td>
                  <td className="px-4 py-3 text-sm">
                    <button
                      onClick={() => handleEditConfig(config)}
                      className="text-purple-primary hover:underline mr-3"
                    >
                      Изменить
                    </button>
                    <button
                      onClick={() => handleDeleteConfig(config.id)}
                      className="text-red-600 hover:underline"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Test Payment Section */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Тестовый платёж</h2>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Shop ID
              </label>
              <input
                type="number"
                value={testPayment.shop_id}
                onChange={e => setTestPayment({...testPayment, shop_id: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Телефон
              </label>
              <input
                type="text"
                value={testPayment.phone}
                onChange={e => setTestPayment({...testPayment, phone: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Сумма (₸)
              </label>
              <input
                type="number"
                value={testPayment.amount}
                onChange={e => setTestPayment({...testPayment, amount: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Сообщение
              </label>
              <input
                type="text"
                value={testPayment.message}
                onChange={e => setTestPayment({...testPayment, message: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <button
            onClick={handleTestPayment}
            className="px-4 py-2 bg-green-success text-white rounded-lg hover:bg-green-600 transition mr-3"
          >
            Создать платёж
          </button>

          {testResult?.data?.external_id && (
            <button
              onClick={handleCheckStatus}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              Проверить статус
            </button>
          )}

          {/* Test result */}
          {testResult && !testResult.loading && (
            <div className={`mt-4 p-4 rounded-lg ${testResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
              <pre className="text-xs overflow-auto">
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">
              {editingConfig ? 'Редактировать' : 'Добавить'} конфигурацию
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Shop ID
                </label>
                <input
                  type="number"
                  value={formData.shop_id}
                  onChange={e => setFormData({...formData, shop_id: e.target.value})}
                  disabled={editingConfig}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  БИН (12 цифр)
                </label>
                <input
                  type="text"
                  value={formData.organization_bin}
                  onChange={e => setFormData({...formData, organization_bin: e.target.value})}
                  disabled={editingConfig}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono disabled:bg-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Описание
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={e => setFormData({...formData, is_active: e.target.checked})}
                  className="mr-2"
                />
                <label className="text-sm font-medium text-gray-700">
                  Активен
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                Отмена
              </button>
              <button
                onClick={handleSaveConfig}
                className="px-4 py-2 bg-purple-primary text-white rounded-lg hover:bg-purple-700 transition"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      <BottomNavBar activeNav={activeNav} onNavChange={handleNavChange} />
    </div>
  );
};

export default PaymentConfigs;
