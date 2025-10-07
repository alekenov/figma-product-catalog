import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { productAPI } from './api/superadmin';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import './App.css';

const ProductsList = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('profile'); // Using profile tab for superadmin
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthError, setIsAuthError] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [shopFilter, setShopFilter] = useState('');
  const [enabledFilter, setEnabledFilter] = useState('all'); // all, enabled, disabled
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Fetch products from API
  useEffect(() => {
    fetchProducts();
  }, [shopFilter, enabledFilter]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100
      };

      if (shopFilter) {
        params.shop_id = parseInt(shopFilter);
      }

      if (enabledFilter === 'enabled') {
        params.enabled = true;
      } else if (enabledFilter === 'disabled') {
        params.enabled = false;
      }

      const data = await productAPI.list(params);
      setProducts(data);
      setError(null);
      setIsAuthError(false);
    } catch (err) {
      console.error('Failed to fetch products:', err);
      // Check if it's an auth error
      const isAuthMsg = err.message?.includes('Сессия истекла') ||
                        err.message?.includes('Необходима авторизация') ||
                        err.message?.includes('Недостаточно прав');
      setIsAuthError(isAuthMsg);
      setError(err.message || 'Не удалось загрузить товары');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (productId) => {
    try {
      await productAPI.toggle(productId);
      // Refresh products list
      fetchProducts();
    } catch (err) {
      console.error('Failed to toggle product:', err);
      alert('Ошибка при переключении статуса товара');
    }
  };

  const handleDelete = async (productId, productName) => {
    if (!window.confirm(`Вы уверены что хотите удалить товар "${productName}"?`)) {
      return;
    }

    try {
      await productAPI.delete(productId);
      // Refresh products list
      fetchProducts();
    } catch (err) {
      console.error('Failed to delete product:', err);
      alert('Ошибка при удалении товара');
    }
  };

  // Filter products by search query
  const filteredProducts = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return products;
    }

    return products.filter(product =>
      product.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.shop_name?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [products, searchQuery]);

  // Format price in tenge
  const formatPrice = (price) => {
    return (price / 100).toLocaleString('ru-RU', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  const statusFilters = [
    { id: 'all', label: 'Все товары' },
    { id: 'enabled', label: 'Активные' },
    { id: 'disabled', label: 'Отключенные' }
  ];

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

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/superadmin')}
            className="text-black text-xl"
          >
            ←
          </button>
          <h1 className="text-[24px] font-['Open_Sans'] font-normal">Товары</h1>
        </div>
        <div className="flex items-center gap-4">
          {/* Search Toggle */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск товаров"
            enabled={products.length > 0}
            isExpanded={isSearchExpanded}
            onExpandedChange={setIsSearchExpanded}
          />
        </div>
      </div>

      {/* Search Input Row - Shows below header when expanded */}
      {isSearchExpanded && (
        <SearchInput
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          placeholder="Поиск по названию или магазину"
          onClose={() => {
            if (!searchQuery.trim()) {
              setIsSearchExpanded(false);
            }
          }}
          inputRef={searchInputRef}
        />
      )}

      {/* Status Filter Pills */}
      <div className="flex gap-2 px-4 mt-6 overflow-x-auto">
        {statusFilters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setEnabledFilter(filter.id)}
            className={`px-3 py-1.5 rounded-full text-[14px] font-['Open_Sans'] font-normal whitespace-nowrap ${
              enabledFilter === filter.id
                ? 'bg-purple-primary text-white'
                : 'bg-purple-light text-black'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Shop Filter Input */}
      <div className="px-4 mt-4">
        <input
          type="number"
          placeholder="Фильтр по ID магазина"
          value={shopFilter}
          onChange={(e) => setShopFilter(e.target.value)}
          className="w-full px-3 py-2 border border-gray-border rounded-lg text-[14px] font-['Open_Sans'] focus:outline-none focus:border-purple-primary"
        />
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка товаров...</div>
        </div>
      )}

      {/* Auth error - friendly prompt */}
      {error && isAuthError && (
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-4">
            Войдите в систему, чтобы увидеть товары
          </div>
          <button
            onClick={() => navigate('/login')}
            className="bg-purple-primary text-white px-6 py-2 rounded-lg font-['Open_Sans'] text-sm hover:bg-purple-600 transition-colors"
          >
            Войти
          </button>
        </div>
      )}

      {/* Other errors - soft message */}
      {error && !isAuthError && (
        <div className="flex flex-col justify-center items-center py-8 px-6 text-center">
          <div className="text-gray-placeholder text-base mb-2">
            Не удалось загрузить данные
          </div>
          <div className="text-gray-400 text-sm mb-4">
            {error}
          </div>
          <button
            onClick={fetchProducts}
            className="bg-purple-primary text-white px-4 py-2 rounded-lg font-['Open_Sans'] text-sm"
          >
            Повторить
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredProducts.length === 0 && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Товары не найдены' : 'Товаров пока нет'}
          </div>
        </div>
      )}

      {/* Products count */}
      {!loading && !error && filteredProducts.length > 0 && (
        <div className="px-4 mt-6 mb-2">
          <span className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
            Найдено товаров: {filteredProducts.length}
          </span>
        </div>
      )}

      {/* Products List */}
      <div className="mt-2">
        {!loading && !error && filteredProducts.map((product) => (
          <div key={product.id}>
            {/* Divider */}
            <div className="border-t border-gray-border"></div>

            {/* Product Item */}
            <div className="px-4 py-4">
              <div className="flex items-start justify-between gap-4">
                {/* Product Info */}
                <div className="flex-1">
                  {/* Product Name and Status */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-[16px] font-['Open_Sans'] font-bold text-black">
                      {product.name}
                    </h3>
                    <span className={`px-2 py-1 rounded text-[12px] font-['Open_Sans'] font-normal ${
                      product.enabled
                        ? 'bg-green-success text-white'
                        : 'bg-gray-400 text-white'
                    }`}>
                      {product.enabled ? 'Активен' : 'Отключен'}
                    </span>
                  </div>

                  {/* Shop Name */}
                  <p className="text-[14px] font-['Open_Sans'] text-gray-placeholder mb-1">
                    <span className="font-semibold">Магазин:</span> {product.shop_name} (ID: {product.shop_id})
                  </p>

                  {/* Price */}
                  <p className="text-[16px] font-['Open_Sans'] font-bold text-black mb-2">
                    {formatPrice(product.price)} ₸
                  </p>

                  {/* Description */}
                  {product.description && (
                    <p className="text-[13px] font-['Open_Sans'] text-gray-placeholder">
                      {product.description.length > 100
                        ? product.description.substring(0, 100) + '...'
                        : product.description}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleToggle(product.id)}
                    className={`px-3 py-1.5 rounded-lg text-[13px] font-['Open_Sans'] font-normal text-white whitespace-nowrap ${
                      product.enabled ? 'bg-status-pink' : 'bg-green-success'
                    }`}
                    title={product.enabled ? 'Отключить товар' : 'Включить товар'}
                  >
                    {product.enabled ? 'Отключить' : 'Включить'}
                  </button>

                  <button
                    onClick={() => handleDelete(product.id, product.name)}
                    className="px-3 py-1.5 bg-red-500 text-white rounded-lg text-[13px] font-['Open_Sans'] font-normal whitespace-nowrap"
                    title="Удалить товар"
                  >
                    Удалить
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Final divider */}
        {!loading && !error && filteredProducts.length > 0 && (
          <div className="border-t border-gray-border"></div>
        )}
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

export default ProductsList;
