import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './App.css';
import { API_BASE_URL } from './services/api';

// Currency conversion helpers
const kopecksToTenge = (kopecks) => {
  if (typeof kopecks !== 'number' || isNaN(kopecks)) return 0;
  return Math.floor(kopecks / 100);
};

const tengeToKopecks = (tenge) => {
  if (typeof tenge !== 'number' || isNaN(tenge)) return 0;
  return Math.floor(tenge * 100);
};

// Helper to detect if value is likely in kopecks (>=100) or tenge (<100)
const detectAndConvertToTenge = (price) => {
  if (typeof price !== 'number' || isNaN(price)) return 0;
  // If price is >= 100, assume it's in kopecks and convert
  // If price is < 100, assume it's already in tenge (backward compatibility)
  return price >= 100 ? kopecksToTenge(price) : price;
};

// Helper to detect if value needs conversion to kopecks for API
const convertToKopecksForAPI = (price) => {
  if (typeof price !== 'number' || isNaN(price)) return 0;
  // If price is < 100, assume it's in tenge and convert to kopecks
  // If price is >= 100, assume it's already in kopecks
  return price < 100 ? tengeToKopecks(price) : price;
};

// Section header component to match OrderDetail
const SectionHeader = ({ title }) => (
  <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px] mb-4">{title}</h2>
);

function WarehouseItemDetail() {
  const navigate = useNavigate();
  const { itemId } = useParams();

  const [warehouseItem, setWarehouseItem] = useState(null);
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [writeOffAmount, setWriteOffAmount] = useState('');
  const [writeOffReason, setWriteOffReason] = useState('');

  useEffect(() => {
    fetchWarehouseItem();
  }, [itemId]);

  const fetchWarehouseItem = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/warehouse/${itemId}`);
      if (!response.ok) throw new Error('Failed to fetch warehouse item');
      const data = await response.json();
      // Convert API response from kopecks to tenge for display
      const convertedData = {
        ...data,
        cost_price: detectAndConvertToTenge(data.cost_price),
        retail_price: detectAndConvertToTenge(data.retail_price)
      };
      setWarehouseItem(convertedData);
      setOperations(data.operations || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching warehouse item:', err);
    } finally {
      setLoading(false);
    }
  };

  // Расчет маржи (использует копейки для точности)
  const calculateMargin = (cost, retail) => {
    // Convert to kopecks for precision calculations
    const costInKopecks = convertToKopecksForAPI(cost);
    const retailInKopecks = convertToKopecksForAPI(retail);

    if (retailInKopecks === 0) return 0;
    return ((retailInKopecks - costInKopecks) / retailInKopecks * 100).toFixed(1);
  };

  // Расчет наценки (использует копейки для точности)
  const calculateMarkup = (cost, retail) => {
    // Convert to kopecks for precision calculations
    const costInKopecks = convertToKopecksForAPI(cost);
    const retailInKopecks = convertToKopecksForAPI(retail);

    if (costInKopecks === 0) return 0;
    return ((retailInKopecks - costInKopecks) / costInKopecks * 100).toFixed(1);
  };

  // Обновление цен через API (конвертирует тенге в копейки)
  const updatePrices = async (field, value) => {
    try {
      const updateData = {};
      // Convert tenge input to kopecks for API storage
      const valueInKopecks = tengeToKopecks(parseFloat(value) || 0);
      updateData[field] = valueInKopecks;

      const response = await fetch(`${API_BASE_URL}/warehouse/${itemId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) throw new Error('Failed to update prices');
      // Refresh the full item data after successful update
      fetchWarehouseItem();
    } catch (err) {
      console.error('Error updating prices:', err);
      alert('Ошибка при обновлении цены');
    }
  };

  const handleCostPriceChange = (value) => {
    setWarehouseItem(prev => ({ ...prev, cost_price: parseFloat(value) || 0 }));
  };

  const handleCostPriceBlur = () => {
    updatePrices('cost_price', warehouseItem.cost_price);
  };

  const handleRetailPriceChange = (value) => {
    setWarehouseItem(prev => ({ ...prev, retail_price: parseFloat(value) || 0 }));
  };

  const handleRetailPriceBlur = () => {
    updatePrices('retail_price', warehouseItem.retail_price);
  };

  const handleMarginChange = (value) => {
    const newMargin = parseFloat(value) || 0;
    const costInKopecks = convertToKopecksForAPI(warehouseItem.cost_price);
    const newRetailPriceInKopecks = costInKopecks / (1 - newMargin / 100);
    const newRetailPriceInTenge = kopecksToTenge(Math.round(newRetailPriceInKopecks));
    setWarehouseItem(prev => ({ ...prev, retail_price: newRetailPriceInTenge }));
  };

  const handleMarginBlur = () => {
    updatePrices('retail_price', warehouseItem.retail_price);
  };

  const handleWriteOff = async () => {
    const amount = parseInt(writeOffAmount);

    if (!amount || amount <= 0) {
      alert('Введите корректное количество для списания');
      return;
    }

    if (amount > warehouseItem.quantity) {
      alert('Нельзя списать больше, чем есть на складе');
      return;
    }

    if (!writeOffReason.trim()) {
      alert('Укажите причину списания');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/warehouse/${itemId}/writeoff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          warehouse_item_id: parseInt(itemId),
          operation_type: 'WRITEOFF',
          quantity_change: -amount,
          description: `Списание: ${writeOffReason}`,
          reason: writeOffReason
        })
      });

      if (!response.ok) throw new Error('Failed to write off');

      fetchWarehouseItem();
      setWriteOffAmount('');
      setWriteOffReason('');
    } catch (err) {
      console.error('Error writing off:', err);
      alert('Ошибка при списании товара');
    }
  };

  const getOperationColor = (type) => {
    switch(type?.toLowerCase()) {
      case 'delivery': return 'text-green-success';
      case 'sale': return 'text-purple-primary';
      case 'writeoff': return 'text-red-500';
      case 'price_change': return 'text-blue-500';
      case 'inventory': return 'text-orange-500';
      default: return 'text-gray-placeholder';
    }
  };

  const getOperationIcon = (type) => {
    switch(type?.toLowerCase()) {
      case 'delivery': return '+';
      case 'sale': return '−';
      case 'writeoff': return '×';
      case 'price_change': return '₸';
      case 'inventory': return '📋';
      default: return '';
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).replace(',', '');
  };

  if (loading) {
    return (
      <div className="figma-container bg-white">
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder font-['Open_Sans']">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error || !warehouseItem) {
    return (
      <div className="figma-container bg-white">
        <div className="px-4 py-6">
          <div className="text-center py-8 text-red-500 font-['Open_Sans']">
            Ошибка: {error || 'Товар не найден'}
          </div>
          <button
            onClick={() => navigate('/warehouse')}
            className="w-full bg-purple-primary text-white py-3 rounded font-['Open_Sans'] uppercase tracking-wider"
          >
            Вернуться к списку
          </button>
        </div>
      </div>
    );
  }

  const margin = calculateMargin(warehouseItem.cost_price, warehouseItem.retail_price);
  const markup = calculateMarkup(warehouseItem.cost_price, warehouseItem.retail_price);

  return (
    <div className="figma-container bg-white">
      {/* Header - matching OrderDetail style */}
      <div className="bg-white border-b border-gray-border px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/warehouse')}
            className="w-6 h-6 flex items-center justify-center"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <h1 className="text-xl font-['Open_Sans']">{warehouseItem.name}</h1>
        </div>
        {warehouseItem.quantity <= warehouseItem.min_quantity && (
          <div className="bg-red-500 px-3 py-1 rounded-full">
            <span className="text-white text-xs font-['Open_Sans'] uppercase tracking-wider">Мало</span>
          </div>
        )}
      </div>

      {/* Product image and basic info */}
      <div className="px-4 pt-4 pb-6 flex items-center gap-3 border-b border-gray-border">
        <div className="relative w-[88px] h-[88px] flex-shrink-0">
          <img
            src={warehouseItem.image}
            alt={warehouseItem.name}
            className="w-full h-full object-cover rounded"
          />
        </div>
        <div className="flex-1">
          <div className="text-sm font-['Open_Sans'] text-gray-disabled">Текущий остаток</div>
          <div className={`text-2xl font-['Open_Sans'] font-bold ${
            warehouseItem.quantity <= warehouseItem.min_quantity ? 'text-red-500' : 'text-black'
          }`}>
            {warehouseItem.quantity} шт
          </div>
          <div className="text-xs font-['Open_Sans'] text-gray-disabled mt-1">
            Мин. остаток: {warehouseItem.min_quantity} шт
          </div>
        </div>
      </div>

      {/* Price section */}
      <div className="px-4 pb-6">
        <SectionHeader title="Ценообразование" />

        <div className="space-y-4">
          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Себестоимость</div>
            <div className="flex items-center justify-between">
              <input
                type="number"
                value={warehouseItem.cost_price}
                onChange={(e) => handleCostPriceChange(e.target.value)}
                onBlur={handleCostPriceBlur}
                className="text-base font-['Open_Sans'] text-black bg-transparent border-b border-gray-border focus:border-purple-primary outline-none w-24"
              />
              <span className="text-base font-['Open_Sans'] text-black">₸</span>
            </div>
          </div>

          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Розничная цена</div>
            <div className="flex items-center justify-between">
              <input
                type="number"
                value={warehouseItem.retail_price}
                onChange={(e) => handleRetailPriceChange(e.target.value)}
                onBlur={handleRetailPriceBlur}
                className="text-base font-['Open_Sans'] text-black bg-transparent border-b border-gray-border focus:border-purple-primary outline-none w-24"
              />
              <span className="text-base font-['Open_Sans'] text-black">₸</span>
            </div>
          </div>

          <div className="border-b border-gray-border pb-4">
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Маржа</div>
            <div className="flex items-center justify-between">
              <input
                type="number"
                value={margin}
                onChange={(e) => handleMarginChange(e.target.value)}
                onBlur={handleMarginBlur}
                className="text-base font-['Open_Sans'] text-black bg-transparent border-b border-gray-border focus:border-purple-primary outline-none w-24"
              />
              <span className="text-base font-['Open_Sans'] text-black">%</span>
            </div>
          </div>

          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-1">Наценка</div>
            <div className="text-base font-['Open_Sans'] font-bold text-purple-primary">{markup}%</div>
          </div>
        </div>
      </div>

      {/* Write-off section */}
      <div className="px-4 pb-6">
        <SectionHeader title="Списание товара" />

        <div className="space-y-4">
          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-2">Количество для списания</div>
            <input
              type="number"
              value={writeOffAmount}
              onChange={(e) => setWriteOffAmount(e.target.value)}
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-border rounded font-['Open_Sans'] focus:border-purple-primary outline-none"
            />
          </div>

          <div>
            <div className="text-sm font-['Open_Sans'] text-gray-disabled mb-2">Причина списания</div>
            <select
              value={writeOffReason}
              onChange={(e) => setWriteOffReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-border rounded font-['Open_Sans'] focus:border-purple-primary outline-none"
            >
              <option value="">Выберите причину</option>
              <option value="Порча">Порча</option>
              <option value="Истек срок">Истек срок</option>
              <option value="Брак">Брак</option>
              <option value="Потеря">Потеря</option>
              <option value="Другое">Другое</option>
            </select>
          </div>

          <button
            onClick={handleWriteOff}
            className="w-full bg-red-500 text-white py-3 rounded font-['Open_Sans'] uppercase tracking-wider hover:bg-red-600 transition-colors"
          >
            Списать
          </button>
        </div>
      </div>

      {/* Operations history */}
      <div className="px-4 pb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-['Open_Sans'] text-black leading-[30px]">История операций</h2>
          <svg className="w-3 h-3 text-gray-400 rotate-90" fill="currentColor" viewBox="0 0 10 10">
            <path d="M5 7L1 3h8L5 7z"/>
          </svg>
        </div>

        <div className="space-y-3">
          {operations.map(op => (
            <div key={op.id} className="pb-3 border-b border-gray-border last:border-0">
              <div className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-['Open_Sans'] font-bold bg-gray-input ${getOperationColor(op.operation_type)}`}>
                  {getOperationIcon(op.operation_type)}
                </div>

                <div className="flex-1">
                  <div className="text-base font-['Open_Sans'] text-black">{op.description}</div>
                  <div className="text-sm font-['Open_Sans'] text-gray-disabled mt-1">
                    {formatDateTime(op.created_at)}
                  </div>
                </div>

                <div className="text-right">
                  {op.quantity_change !== 0 && (
                    <div className={`text-base font-['Open_Sans'] font-bold ${
                      op.quantity_change > 0 ? 'text-green-success' : 'text-red-500'
                    }`}>
                      {op.quantity_change > 0 ? '+' : ''}{op.quantity_change} шт
                    </div>
                  )}
                  <div className="text-sm font-['Open_Sans'] text-gray-disabled">
                    Остаток: {op.balance_after} шт
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {operations.length === 0 && (
          <div className="text-center py-4 text-gray-placeholder font-['Open_Sans']">
            Нет операций
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="px-4 pb-6">
        <button
          onClick={() => navigate('/warehouse')}
          className="w-full bg-white border border-gray-border text-black py-3 rounded font-['Open_Sans'] uppercase tracking-wider mb-3"
        >
          Назад к складу
        </button>
      </div>
    </div>
  );
}

export default WarehouseItemDetail;
