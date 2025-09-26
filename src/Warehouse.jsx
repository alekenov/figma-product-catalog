import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from './components/BottomNavBar';
import InventoryIcon from './components/InventoryIcon';
import './App.css';

// Currency conversion helpers
const kopecksToTenge = (kopecks) => {
  if (typeof kopecks !== 'number' || isNaN(kopecks)) return 0;
  return Math.floor(kopecks / 100);
};

// Helper to detect if value is likely in kopecks (>=100) or tenge (<100)
const detectAndConvertPrice = (price) => {
  if (typeof price !== 'number' || isNaN(price)) return 0;
  // If price is >= 100, assume it's in kopecks and convert
  // If price is < 100, assume it's already in tenge (backward compatibility)
  return price >= 100 ? kopecksToTenge(price) : price;
};

function Warehouse() {
  const navigate = useNavigate();
  const [warehouseItems, setWarehouseItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageErrors, setImageErrors] = useState({});

  useEffect(() => {
    fetchWarehouseItems();
  }, []);

  const fetchWarehouseItems = async () => {
    try {
      const response = await fetch('http://localhost:8012/api/v1/warehouse/');
      if (!response.ok) throw new Error('Failed to fetch warehouse items');
      const data = await response.json();
      setWarehouseItems(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching warehouse items:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Нет данных';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const handleImageError = (itemId) => {
    setImageErrors(prev => ({ ...prev, [itemId]: true }));
  };

  if (loading) {
    return (
      <div className="figma-container">
        <div className="px-4 py-6">
          <h1 className="text-xl font-semibold mb-6">Склад</h1>
          <div className="text-center py-8 text-gray-placeholder">Загрузка...</div>
        </div>
        <BottomNavBar activeTab="warehouse" onTabChange={(id, route) => navigate(route)} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="figma-container">
        <div className="px-4 py-6">
          <h1 className="text-xl font-semibold mb-6">Склад</h1>
          <div className="text-center py-8 text-red-500">Ошибка: {error}</div>
        </div>
        <BottomNavBar activeTab="warehouse" onTabChange={(id, route) => navigate(route)} />
      </div>
    );
  }

  return (
    <div className="figma-container bg-white">
      {/* Header section - matching Orders page */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Склад</h1>
        <div className="flex items-center gap-2">
          <button
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center"
            onClick={() => navigate('/warehouse/inventory')}
            title="Инвентаризация"
          >
            <InventoryIcon className="w-4 h-4" color="white" />
          </button>
          <button
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center"
            onClick={() => navigate('/warehouse/add-inventory')}
            title="Добавить товар"
          >
            <span className="text-white text-lg leading-none">+</span>
          </button>
        </div>
      </div>

      {/* Items list - styled like Orders list */}
      <div className="mt-6">
        {warehouseItems.map((item) => (
          <div
            key={item.id}
            className="px-4 py-3 border-b border-gray-border cursor-pointer hover:bg-gray-50 transition-all hover:shadow-sm"
            onClick={() => navigate(`/warehouse/${item.id}`)}
          >
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-3">
                {/* Product image with fallback */}
                <div className="relative flex-shrink-0">
                  {imageErrors[item.id] ? (
                    // Fallback placeholder when image fails to load
                    <div className="w-[72px] h-[88px] bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  ) : (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="w-[72px] h-[88px] object-cover rounded-lg shadow-sm"
                      onError={() => handleImageError(item.id)}
                    />
                  )}
                  {item.quantity <= item.min_quantity && (
                    <div className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-['Open_Sans'] font-medium px-2 py-0.5 rounded-full shadow-sm">
                      Мало
                    </div>
                  )}
                </div>

                {/* Item info - left column */}
                <div className="flex-1">
                  <h3 className="text-base font-['Open_Sans'] font-semibold text-gray-900 mb-1">
                    {item.name}
                  </h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-['Open_Sans'] font-medium text-purple-primary">
                      {detectAndConvertPrice(item.retail_price)} ₸
                    </span>
                    <span className="text-xs font-['Open_Sans'] text-gray-disabled">
                      за шт
                    </span>
                  </div>
                  <div className="text-xs font-['Open_Sans'] text-gray-disabled mt-1">
                    Поставка: {formatDate(item.last_delivery_date)}
                  </div>
                </div>
              </div>

              {/* Right column - quantity */}
              <div className="text-right ml-4">
                <div className={`text-xl font-['Open_Sans'] font-bold ${
                  item.quantity <= item.min_quantity ? 'text-red-500' : 'text-gray-900'
                }`}>
                  {item.quantity}
                </div>
                <div className="text-xs font-['Open_Sans'] text-gray-disabled">
                  шт
                </div>
              </div>
            </div>
          </div>
        ))}

        {warehouseItems.length === 0 && (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-placeholder font-['Open_Sans']">
              Нет товаров на складе
            </div>
          </div>
        )}
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-20" />

      {/* Bottom Navigation */}
      <BottomNavBar
        activeTab="warehouse"
        onTabChange={(id, route) => navigate(route)}
      />
    </div>
  );
}

export default Warehouse;