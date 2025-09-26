import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ToggleSwitch from './components/ToggleSwitch';
import BottomNavBar from './components/BottomNavBar';
import './App.css';

const ReadyProducts = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('products');
  const [searchQuery, setSearchQuery] = useState('');

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

  // Фильтрация товаров по поиску
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="figma-container bg-white">

      {/* Заголовок и кнопка добавления */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Товары</h1>
        <button
          onClick={() => navigate('/add-product')}
          className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
          <span className="text-white text-lg leading-none">+</span>
        </button>
      </div>

      {/* Поле поиска */}
      <div className="px-4 mt-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Найти"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 bg-[#EEEDF2] rounded-lg text-base font-['Open_Sans'] placeholder-[#828282] outline-none pr-10"
          />
          <svg className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4" fill="none" stroke="#828282" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" strokeWidth="2"/>
            <path strokeWidth="2" strokeLinecap="round" d="M21 21l-4.35-4.35"/>
          </svg>
        </div>
      </div>

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
                <div className="mx-4 border-t border-[#E0E0E0]"></div>
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
                      !isEnabled ? 'text-[#6B6773]' : 'text-black'
                    }`}>
                      {product.name}
                    </h3>
                    <p className={`text-sm font-['Open_Sans'] mt-2 ${
                      !isEnabled ? 'text-[#6B6773]' : 'text-black'
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
              <div className="mx-4 border-t border-[#E0E0E0]"></div>
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