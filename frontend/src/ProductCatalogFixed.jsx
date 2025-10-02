import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ToggleSwitch from './components/ToggleSwitch';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import SearchInput from './components/SearchInput';
import FilterHeader from './components/FilterHeader';
import LoadingSpinner from './components/LoadingSpinner';
import { useProducts, useUpdateProduct } from './hooks/useProducts';
import { productsAPI } from './services/api';
import './App.css';

const ProductCatalogFixed = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('products');
  const [activeFilters, setActiveFilters] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [productStates, setProductStates] = useState({});
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchInputRef = useRef(null);

  // Use React Query hooks
  const { data: allProducts = [], isLoading: loading, error } = useProducts({ enabled_only: false });
  const updateProduct = useUpdateProduct();

  const handleNavChange = (navId, route) => {
    setActiveNav(navId);
    navigate(route);
  };

  // Загружаем фильтры из localStorage при монтировании
  React.useEffect(() => {
    const savedFilters = localStorage.getItem('productFilters');
    if (savedFilters) {
      setActiveFilters(JSON.parse(savedFilters));
    }
  }, []);

  // Initialize product states when allProducts loads
  useEffect(() => {
    if (allProducts.length > 0) {
      const initialStates = allProducts.reduce((acc, product) => ({
        ...acc,
        [product.id]: product.enabled
      }), {});
      setProductStates(initialStates);
    }
  }, [allProducts]);

  // Применяем фильтры и поиск к товарам
  const products = React.useMemo(() => {
    let filteredProducts = allProducts;

    // Применяем фильтры по типу
    if (activeFilters) {
      const hasActiveFilters = Object.values(activeFilters.productTypes).some(v => v);
      if (hasActiveFilters) {
        filteredProducts = filteredProducts.filter(product => {
          return activeFilters.productTypes[product.type];
        });
      }
    }

    // Применяем поиск
    if (searchQuery.trim()) {
      filteredProducts = filteredProducts.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filteredProducts;
  }, [allProducts, activeFilters, searchQuery]);

  const toggleProduct = async (productId) => {
    const currentState = productStates[productId];
    const newState = !currentState;

    // Optimistically update UI
    setProductStates(prev => ({
      ...prev,
      [productId]: newState
    }));

    // Update via React Query mutation
    updateProduct.mutate(
      {
        id: productId,
        data: { enabled: newState }
      },
      {
        onError: (err) => {
          console.error('Failed to toggle product status:', err);
          // Revert optimistic update on error
          setProductStates(prev => ({
            ...prev,
            [productId]: currentState
          }));
        }
      }
    );
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

  // Show loading spinner for initial load
  if (loading && allProducts.length === 0) {
    return <LoadingSpinner />;
  }

  // Check if error is auth-related
  const isAuthError = error && (
    error.message?.includes('Сессия истекла') ||
    error.message?.includes('Необходима авторизация') ||
    error.message?.includes('Недостаточно прав')
  );

  // Show friendly auth prompt for auth errors
  if (error && isAuthError) {
    return (
      <div className="figma-container bg-white">
        <div className="flex items-center justify-between px-4 mt-5">
          <h1 className="text-2xl font-['Open_Sans'] font-normal">Товары</h1>
        </div>
        <div className="flex flex-col justify-center items-center py-12 px-6 text-center mt-20">
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
        <BottomNavBar
          activeTab={activeNav}
          onTabChange={handleNavChange}
        />
      </div>
    );
  }

  const errorMessage = error ? 'Не удалось загрузить товары' : null;

  return (
    <div className="figma-container bg-white">{/* Content container without top tabs */}

      {/* Заголовок с кнопками */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Товары</h1>
        <div className="flex items-center gap-4">
          {/* Search Toggle (collapsed state shows icon in header) */}
          <SearchToggle
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            placeholder="Поиск товаров"
            enabled={allProducts.length > 0}
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
      <FilterHeader
        type="shop"
        label="Магазин Cvety.kz"
        onFiltersClick={() => navigate('/filters')}
      />

      {/* Error state */}
      {errorMessage && (
        <div className="flex justify-center items-center py-8">
          <div className="text-red-500">{errorMessage}</div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !errorMessage && products.length === 0 && (
        <div className="flex flex-col justify-center items-center py-8 px-6 text-center">
          <div className="text-gray-placeholder text-base">
            {searchQuery ? 'Товары не найдены' : 'Товаров пока нет'}
          </div>
          {!searchQuery && (
            <div className="text-gray-400 text-sm mt-2">
              Добавьте первый товар, нажав на кнопку +
            </div>
          )}
        </div>
      )}

      {/* Список товаров */}
      <div className="mt-6">
        {!loading && !errorMessage && products.map((product, index) => {
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
                  {/* Изображение товара - кликабельное */}
                  <div
                    className="relative w-[88px] h-[88px] flex-shrink-0 cursor-pointer"
                    onClick={() => navigate(`/product/${product.id}`)}
                  >
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover rounded"
                    />
                    {!isEnabled && (
                      <div className="absolute inset-0 bg-white bg-opacity-60 rounded"></div>
                    )}
                  </div>

                  {/* Информация о товаре - кликабельная */}
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => navigate(`/product/${product.id}`)}
                  >
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

export default ProductCatalogFixed;