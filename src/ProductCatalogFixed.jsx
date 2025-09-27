import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ToggleSwitch from './components/ToggleSwitch';
import BottomNavBar from './components/BottomNavBar';
import SearchToggle from './components/SearchToggle';
import FilterHeader from './components/FilterHeader';
import LoadingSpinner from './components/LoadingSpinner';
import { useProducts, useUpdateProduct } from './hooks/useProducts';
import { productsAPI } from './services/api';
import './App.css';

// Изображения букетов из Figma
const imgRectangle = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__";
const imgRectangle1 = "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__";

const ProductCatalogFixed = () => {
  const navigate = useNavigate();
  const [activeNav, setActiveNav] = useState('products');
  const [activeFilters, setActiveFilters] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [productStates, setProductStates] = useState({});

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

  // Show loading spinner for initial load
  if (loading && allProducts.length === 0) {
    return <LoadingSpinner />;
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
          />
          {/* Add Product Button */}
          <button
            onClick={() => navigate('/add-product')}
            className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
            <span className="text-white text-lg leading-none">+</span>
          </button>
        </div>
      </div>

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
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">
            {searchQuery ? 'Товары не найдены' : 'Товаров пока нет'}
          </div>
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