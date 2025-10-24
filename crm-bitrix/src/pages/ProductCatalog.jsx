import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ToggleSwitch from '../components/ToggleSwitch';
import SearchToggle from '../components/SearchToggle';
import SearchInput from '../components/SearchInput';
import LoadingSpinner from '../components/LoadingSpinner';
import BottomNavBar from '../components/BottomNavBar';
import { productsAPI } from '../services';
import '../App.css';

const ProductCatalog = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [productStates, setProductStates] = useState({});
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const searchInputRef = useRef(null);

  // Fetch products from Bitrix API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await productsAPI.getProducts({ limit: 20 });
        setProducts(response.products);

        // Initialize product states (enabled/disabled)
        const initialStates = response.products.reduce((acc, product) => ({
          ...acc,
          [product.id]: product.enabled
        }), {});
        setProductStates(initialStates);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch products:', err);
        setError(err.message || 'Не удалось загрузить товары');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Filter products by search query
  const filteredProducts = React.useMemo(() => {
    let filtered = products;

    if (searchQuery.trim()) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [products, searchQuery]);

  const toggleProduct = async (productId) => {
    const currentState = productStates[productId];
    const newState = !currentState;
    const product = products.find((item) => item.id === productId);

    if (!product) {
      console.warn(`Product with id ${productId} not found in state`);
      return;
    }

    // Optimistically update UI
    setProductStates(prev => ({
      ...prev,
      [productId]: newState
    }));
    setProducts(prev => prev.map(item => item.id === productId ? { ...item, enabled: newState } : item));

    try {
      // Update via API and sync state with response
      const updatedProduct = await productsAPI.toggleProductStatus(productId, newState);

      setProducts(prev => prev.map(item => (
        item.id === productId ? { ...item, ...updatedProduct } : item
      )));
      setProductStates(prev => ({
        ...prev,
        [productId]: updatedProduct.enabled
      }));
    } catch (err) {
      console.error('Failed to toggle product status:', err);
      // Revert optimistic update on error
      setProductStates(prev => ({
        ...prev,
        [productId]: currentState
      }));
      setProducts(prev => prev.map(item => item.id === productId ? { ...item, enabled: currentState } : item));
    }
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
  if (loading && products.length === 0) {
    return <LoadingSpinner />;
  }

  const handleNavChange = (navId, route) => {
    navigate(route);
  };

  return (
    <div className="figma-container bg-white">

      {/* Header with actions */}
      <div className="flex items-center justify-between px-4 mt-5">
        <h1 className="text-2xl font-['Open_Sans'] font-normal">Товары</h1>
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

      {/* Error state */}
      {error && (
        <div className="flex justify-center items-center py-8">
          <div className="text-red-500">{error}</div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && filteredProducts.length === 0 && (
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

      {/* Products List */}
      <div className="mt-6">
        {!loading && !error && filteredProducts.map((product, index) => {
          const isEnabled = productStates[product.id];
          return (
            <div key={product.id}>
              {/* Divider before product */}
              {index === 0 && (
                <div className="mx-4 border-t border-gray-border"></div>
              )}

              {/* Product */}
              <div className="px-4 py-2">
                <div className="flex items-center gap-3">
                  {/* Product Image - clickable */}
                  <div
                    className="relative w-[88px] h-[88px] flex-shrink-0 cursor-pointer"
                    onClick={() => navigate(`/products/${product.id}`)}
                  >
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover rounded"
                      loading="lazy"
                    />
                    {!isEnabled && (
                      <div className="absolute inset-0 bg-white bg-opacity-60 rounded"></div>
                    )}
                  </div>

                  {/* Product Info - clickable */}
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => navigate(`/products/${product.id}`)}
                  >
                    <h3 className={`text-sm font-['Open_Sans'] font-bold ${
                      !isEnabled ? 'text-gray-disabled' : 'text-black'
                    }`}>
                      {product.name}
                    </h3>
                    <p className={`text-sm font-['Open_Sans'] mt-2 ${
                      !isEnabled ? 'text-gray-disabled' : 'text-black'
                    }`}>
                      {product.price.toLocaleString()} ₸
                    </p>
                  </div>

                  {/* Toggle Switch */}
                  <ToggleSwitch
                    isEnabled={isEnabled}
                    onToggle={() => toggleProduct(product.id)}
                  />
                </div>
              </div>

              {/* Divider after product */}
              <div className="mx-4 border-t border-gray-border"></div>
            </div>
          );
        })}
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-16" />

      {/* Bottom Navigation */}
      <BottomNavBar
        activeTab="products"
        onTabChange={handleNavChange}
      />
    </div>
  );
};

export default ProductCatalog;
