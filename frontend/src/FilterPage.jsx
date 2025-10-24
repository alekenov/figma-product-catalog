import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

const FilterPage = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    productTypes: {
      flowers: true,
      sweets: true,
      fruits: false,
      decorations: false,
      cosmetics: false,
      gifts: false
    },
    availability: 'all', // all, inStock, outOfStock
    showOnlyNew: false // Show only products created within last 7 days
  });

  const handleTypeToggle = (type) => {
    setFilters(prev => ({
      ...prev,
      productTypes: {
        ...prev.productTypes,
        [type]: !prev.productTypes[type]
      }
    }));
  };

  const handleReset = () => {
    setFilters({
      productTypes: {
        flowers: false,
        sweets: false,
        fruits: false,
        decorations: false,
        cosmetics: false,
        gifts: false
      },
      availability: 'all',
      showOnlyNew: false
    });
  };

  const handleApply = () => {
    // Сохраняем фильтры в localStorage или передаем через state
    localStorage.setItem('productFilters', JSON.stringify(filters));
    navigate('/');
  };

  return (
    <div className="figma-container bg-white">
      {/* Заголовок */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-border">
        <button
          onClick={() => navigate('/')}
          className="w-4 h-4 flex items-center justify-center"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12M4 4L12 12" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>
        <h1 className="text-lg font-['Open_Sans'] font-semibold">Фильтры</h1>
        <button
          onClick={handleReset}
          className="text-purple-primary text-sm font-['Open_Sans']"
        >
          Сбросить
        </button>
      </div>

      {/* Тип товара */}
      <div className="px-4 py-6">
        <h2 className="text-lg font-['Open_Sans'] font-semibold mb-6">Тип товара</h2>

        {/* Цветы */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Цветы</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.flowers}
              onChange={() => handleTypeToggle('flowers')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.flowers ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.flowers && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>

        {/* Сладости */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Сладости</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.sweets}
              onChange={() => handleTypeToggle('sweets')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.sweets ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.sweets && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>

        {/* Фрукты и ягоды */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Фрукты и ягоды</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.fruits}
              onChange={() => handleTypeToggle('fruits')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.fruits ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.fruits && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>

        {/* Украшения */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Украшения</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.decorations}
              onChange={() => handleTypeToggle('decorations')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.decorations ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.decorations && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>

        {/* Косметика и парфюмерия */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Косметика и парфюмерия</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.cosmetics}
              onChange={() => handleTypeToggle('cosmetics')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.cosmetics ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.cosmetics && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>

        {/* Подарки */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <span className="text-base font-['Open_Sans']">Подарки</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.productTypes.gifts}
              onChange={() => handleTypeToggle('gifts')}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.productTypes.gifts ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.productTypes.gifts && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>
      </div>

      {/* Разделитель */}
      <div className="border-t border-gray-border"></div>

      {/* Наличие */}
      <div className="px-4 py-6">
        <h2 className="text-lg font-['Open_Sans'] font-semibold mb-6">Наличие</h2>

        {/* Показать только новинки */}
        <label className="flex items-center justify-between py-3 cursor-pointer">
          <div>
            <span className="text-base font-['Open_Sans']">Только новинки</span>
            <p className="text-sm font-['Open_Sans'] text-gray-disabled mt-1">
              Товары за последние 7 дней
            </p>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={filters.showOnlyNew}
              onChange={() => setFilters(prev => ({ ...prev, showOnlyNew: !prev.showOnlyNew }))}
              className="sr-only"
            />
            <div className={`w-6 h-6 rounded-sm ${
              filters.showOnlyNew ? 'bg-purple-primary' : 'border border-gray-disabled'
            }`}>
              {filters.showOnlyNew && (
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="absolute top-1 left-1">
                  <path d="M3 8L6 11L13 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
          </div>
        </label>
      </div>

      {/* Кнопка применить */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-gray-border bg-white p-4">
        <button
          onClick={handleApply}
          className="w-full py-3 bg-purple-primary hover:bg-purple-hover text-white rounded text-sm font-['Open_Sans'] tracking-wider uppercase transition-colors"
        >
          Применить
        </button>
      </div>
    </div>
  );
};

export default FilterPage;