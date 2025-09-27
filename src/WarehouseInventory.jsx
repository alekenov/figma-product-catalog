import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from './components/ToastProvider';
import './App.css';
import { API_BASE_URL } from './services/api';

function WarehouseInventory() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [warehouseItems, setWarehouseItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    conducted_by: 'Администратор',
    comment: '',
    items: {}
  });
  const [showCommentField, setShowCommentField] = useState(false);

  useEffect(() => {
    fetchWarehouseItems();
  }, []);

  const fetchWarehouseItems = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/inventory/prepare/items`);
      if (!response.ok) throw new Error('Failed to fetch warehouse items');
      const data = await response.json();
      setWarehouseItems(data);

      // Initialize form items with empty values for user input
      const items = {};
      data.forEach(item => {
        items[item.id] = '';
      });
      setFormData(prev => ({ ...prev, items }));
    } catch (err) {
      setError(err.message);
      console.error('Error fetching warehouse items:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = (itemId, value) => {
    const quantity = value === '' ? '' : Math.max(0, parseInt(value) || 0);
    setFormData(prev => ({
      ...prev,
      items: {
        ...prev.items,
        [itemId]: quantity
      }
    }));
  };

  const handleCommentChange = (value) => {
    setFormData(prev => ({ ...prev, comment: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Prepare items data for API
      const items = Object.entries(formData.items)
        .filter(([_, quantity]) => quantity !== '')
        .map(([warehouse_item_id, actual_quantity]) => ({
          warehouse_item_id: parseInt(warehouse_item_id),
          actual_quantity: parseInt(actual_quantity)
        }));

      if (items.length === 0) {
        showToast('Необходимо указать хотя бы один остаток', 'error');
        return;
      }

      const inventoryData = {
        conducted_by: formData.conducted_by,
        comment: formData.comment || null,
        items: items
      };

      // Create inventory check
      const createResponse = await fetch(`${API_BASE_URL}/inventory/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inventoryData)
      });

      if (!createResponse.ok) {
        throw new Error('Failed to create inventory check');
      }

      const inventoryCheck = await createResponse.json();

      // Apply inventory check
      const applyResponse = await fetch(`${API_BASE_URL}/inventory/${inventoryCheck.id}/apply`, {
        method: 'POST'
      });

      if (!applyResponse.ok) {
        throw new Error('Failed to apply inventory check');
      }

      showToast('Инвентаризация успешно проведена', 'success');
      navigate('/warehouse');

    } catch (err) {
      console.error('Error submitting inventory:', err);
      showToast(`Ошибка при проведении инвентаризации: ${err.message}`, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const hasChanges = () => {
    return warehouseItems.some(item => {
      const currentQty = formData.items[item.id];
      return currentQty !== '';
    });
  };

  if (loading) {
    return (
      <div className="figma-container">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => navigate('/warehouse')}
              className="text-purple-primary"
            >
              ← Назад
            </button>
            <h1 className="text-xl font-semibold">Инвентаризация</h1>
            <div></div>
          </div>
          <div className="text-center py-8 text-gray-placeholder">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="figma-container">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => navigate('/warehouse')}
              className="text-purple-primary"
            >
              ← Назад
            </button>
            <h1 className="text-xl font-semibold">Инвентаризация</h1>
            <div></div>
          </div>
          <div className="text-center py-8 text-red-500">Ошибка: {error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5 mb-6">
        <button
          onClick={() => navigate('/warehouse')}
          className="text-purple-primary font-['Open_Sans']"
        >
          ← Назад
        </button>
        <h1 className="text-xl font-['Open_Sans'] font-semibold">Инвентаризация</h1>
        <div></div>
      </div>

      <form onSubmit={handleSubmit} className="px-4">
        {/* Conducted by field */}
        <div className="mb-6">
          <label className="block text-sm font-['Open_Sans'] font-medium text-gray-700 mb-2">
            Проводил инвентаризацию
          </label>
          <input
            type="text"
            value={formData.conducted_by}
            onChange={(e) => setFormData(prev => ({ ...prev, conducted_by: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent"
            required
          />
        </div>

        {/* Items list */}
        <div className="mb-6">
          <h2 className="text-lg font-['Open_Sans'] font-semibold mb-4">Фактические остатки</h2>
          <div className="space-y-3">
            {warehouseItems.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 border border-gray-border rounded-lg"
              >
                <div className="flex items-center space-x-3 flex-1">
                  {/* Item image */}
                  <div className="w-10 h-10 flex-shrink-0">
                    {item.image ? (
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-10 h-10 object-cover rounded-lg"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div
                      className="w-10 h-10 bg-gray-input rounded-lg flex items-center justify-center"
                      style={{ display: item.image ? 'none' : 'flex' }}
                    >
                      <span className="text-gray-disabled text-xs">📦</span>
                    </div>
                  </div>

                  {/* Item name */}
                  <div className="flex-1">
                    <div className="font-['Open_Sans'] font-medium text-gray-900 text-sm">
                      {item.name}
                    </div>
                    <div className="text-xs text-gray-disabled">
                      Учёт: {item.current_quantity} шт
                    </div>
                  </div>
                </div>

                {/* Quantity input */}
                <div className="w-20">
                  <input
                    type="number"
                    min="0"
                    value={formData.items[item.id] || ''}
                    onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    className="w-full px-2 py-1 text-center border border-gray-border rounded focus:outline-none focus:ring-1 focus:ring-purple-primary focus:border-transparent"
                    placeholder="0"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Comment section */}
        <div className="mb-6">
          {!showCommentField ? (
            <button
              type="button"
              onClick={() => setShowCommentField(true)}
              className="text-purple-primary font-['Open_Sans'] text-sm hover:text-purple-600 transition-colors"
            >
              + Добавить комментарий
            </button>
          ) : (
            <div>
              <label className="block text-sm font-['Open_Sans'] font-medium text-gray-700 mb-2">
                Комментарий (необязательно)
              </label>
              <textarea
                value={formData.comment}
                onChange={(e) => handleCommentChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent"
                rows="3"
                placeholder="Дополнительные заметки по инвентаризации..."
                autoFocus
              />
              <button
                type="button"
                onClick={() => {
                  setShowCommentField(false);
                  handleCommentChange('');
                }}
                className="mt-2 text-gray-disabled font-['Open_Sans'] text-xs hover:text-gray-600 transition-colors"
              >
                Скрыть
              </button>
            </div>
          )}
        </div>

        {/* Submit button */}
        <div className="pb-8">
          <button
            type="submit"
            disabled={submitting || !hasChanges()}
            className={`w-full py-3 rounded-lg font-['Open_Sans'] font-medium ${
              submitting || !hasChanges()
                ? 'bg-gray-neutral text-gray-disabled cursor-not-allowed'
                : 'bg-purple-primary text-white hover:bg-purple-600'
            }`}
          >
            {submitting ? 'Обработка...' : 'Принять инвентаризацию'}
          </button>

          {hasChanges() && (
            <div className="mt-2 text-xs text-center text-gray-disabled">
              Остатки будут обновлены в соответствии с фактическими данными
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default WarehouseInventory;
