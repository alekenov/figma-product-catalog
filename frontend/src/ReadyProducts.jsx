import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ToggleSwitch from './components/ToggleSwitch';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import './App.css';

const ReadyProducts = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('products');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  const [products, setProducts] = useState([
    {
      id: 1,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=200&h=200&fit=crop',
      enabled: true
    },
    {
      id: 2,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=200&h=200&fit=crop',
      enabled: true
    },
    {
      id: 3,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=200&h=200&fit=crop',
      enabled: true
    },
    {
      id: 4,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=200&h=200&fit=crop',
      enabled: true
    },
    {
      id: 5,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=200&h=200&fit=crop',
      enabled: false
    },
    {
      id: 6,
      name: 'Готовый товар',
      price: '12 000 ₸',
      image: 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=200&h=200&fit=crop',
      enabled: false
    }
  ]);

  const [productStates, setProductStates] = useState(
    products.reduce((acc, product) => ({ ...acc, [product.id]: product.enabled }), {})
  );

  const toggleProduct = (productId) => {
    setProductStates(prev => ({
      ...prev,
      [productId]: !prev[productId]
    }));
  };

  // Handle search expanded state
  useEffect(() => {
    if (isSearchExpanded && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [isSearchExpanded]);

  // Auto-expand search if there's a query
  useEffect(() => {
    if (searchQuery.trim()) {
      setIsSearchExpanded(true);
    }
  }, [searchQuery]);

  // Фильтрация товаров по поиску
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="figma-container bg-white">

      {/* Заголовок с кнопками */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Товары</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle (collapsed state shows icon in header) */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск товаров"
            enabled={products.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
          {/* Add Product Button */}
          <button
            onClick={() => navigate('/add-product')}
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
            <span className="text-white text-lg leading-none">+</span>
          </button>
        </div>
      </div>

      {/* Search Input Row - Shows below header when expanded */}
      {isSearchExpanded && (
        <SearchInput
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          placeholder="Поиск товаров"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Фильтры */}
      <div className="flex items-center justify-between px-4 mt-6">
        <div className="flex items-center gap-1 text-sm font-['Open_Sans'] text-black">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
            <path strokeWidth="1.5" d="M17 18H3v-9.5A1.5 1.5 0 014.5 7h11A1.5 1.5 0 0117 8.5V18z"/>
            <path strokeWidth="1.5" d="M7 7V4a1 1 0 011-1h4a1 1 0 011 1v3"/>
          </svg>
          <span>Магазин Cvety.kz</span>
        </div>
        <button
          onClick={() => navigate('/filters')}
          className="flex items-center gap-1 text-sm font-['Open_Sans'] text-black">
          <span>Фильтры</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
            <path strokeWidth="1.5" d="M4 3h12l-2 6H6L4 3zM6 9v9M14 9v9M10 9v5"/>
          </svg>
        </button>
      </div>

      {/* Список товаров */}
      <div className="mt-6">
        {filteredProducts.map((product, index) => {
          const isEnabled = productStates[product.id];
          return (
            <div key={product.id}>
              {/* Горизонтальная линия перед товаром */}
              {index === 0 && (
                <div className="mx-4 border-t border-gray-border"></div>
              )}

              {/* Товар */}
              <div className="px-4 py-2">
                <div className="flex items-center gap-3">
                  {/* Изображение товара */}
                  <div className="relative w-[88px] h-[88px] flex-shrink-0">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover rounded"
                    />
                    {!isEnabled && (
                      <div className="absolute inset-0 bg-white bg-opacity-60 rounded"></div>
                    )}
                  </div>

                  {/* Информация о товаре */}
                  <div className="flex-1">
                    <h3 className={`text-sm font-['Open_Sans'] font-bold ${
                      !isEnabled ? 'text-gray-disabled' : 'text-black'
                    }`}>
                      {product.name}
                    </h3>
                    <p className={`text-sm font-['Open_Sans'] mt-2 ${
                      !isEnabled ? 'text-gray-disabled' : 'text-black'
                    }`}>
                      {product.price}
                    </p>
                  </div>

                  {/* Переключатель */}
                  <ToggleSwitch
                    isEnabled={isEnabled}
                    onToggle={() => toggleProduct(product.id)}
                  />
                </div>
              </div>

              {/* Горизонтальная линия после товара */}
              <div className="mx-4 border-t border-gray-border"></div>
            </div>
          );
        })}
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

export default ReadyProducts;