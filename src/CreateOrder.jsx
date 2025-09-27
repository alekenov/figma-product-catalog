import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchToggle from './components/SearchToggle';
import { productsAPI, formatProductForDisplay } from './services/api';
import './App.css';

const CreateOrder = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch products from API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const rawProducts = await productsAPI.getProducts({ limit: 100, enabled_only: true });
        const formattedProducts = rawProducts.map(product => {
          const formatted = formatProductForDisplay(product);
          return {
            ...formatted,
            image: product.image || "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__"
          };
        });
        setProducts(formattedProducts);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch products:', err);
        setError('Не удалось загрузить товары');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Filter products by search query
  const filteredProducts = React.useMemo(() => {
    if (!searchQuery.trim()) {
      return products;
    }
    return products.filter(product =>
      product.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [products, searchQuery]);

  // Handle product selection
  const handleProductToggle = (productId) => {
    setSelectedProducts(prev => {
      const newState = { ...prev };
      if (newState[productId]) {
        delete newState[productId];
      } else {
        newState[productId] = { quantity: 1, product: products.find(p => p.id === productId) };
      }
      return newState;
    });
  };

  // Handle quantity change
  const handleQuantityChange = (productId, delta) => {
    setSelectedProducts(prev => {
      const newState = { ...prev };
      if (newState[productId]) {
        const newQuantity = newState[productId].quantity + delta;
        if (newQuantity > 0) {
          newState[productId] = { ...newState[productId], quantity: newQuantity };
        } else {
          delete newState[productId];
        }
      }
      return newState;
    });
  };

  // Calculate total
  const total = Object.values(selectedProducts).reduce((sum, item) => {
    return sum + (item.product.price * item.quantity);
  }, 0);

  const handleNext = () => {
    if (Object.keys(selectedProducts).length === 0) {
      return;
    }
    // Pass selected products to next step
    navigate('/create-order/customer', {
      state: { selectedProducts, total }
    });
  };

  const handleBack = () => {
    navigate('/orders');
  };

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center px-4 pt-6 pb-4">
        <button onClick={handleBack} className="p-2 -ml-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <h1 className="text-[24px] font-['Open_Sans'] font-normal ml-2">Новый заказ</h1>
      </div>

      {/* Step indicator */}
      <div className="px-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-primary rounded-full flex items-center justify-center text-white text-[14px] font-bold">1</div>
            <span className="text-[14px] font-['Open_Sans'] text-black">Товары</span>
          </div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-gray-neutral rounded-full flex items-center justify-center text-gray-disabled text-[14px] font-bold">2</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Клиент</span>
          </div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-gray-neutral rounded-full flex items-center justify-center text-gray-disabled text-[14px] font-bold">3</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Проверка</span>
          </div>
        </div>
      </div>

      {/* Search - Always expanded for product selection */}
      <SearchToggle
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        placeholder="Поиск товаров..."
        enabled={products.length > 0}
        forceExpanded={true}
      />

      {/* Loading state */}
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-placeholder">Загрузка товаров...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="flex justify-center items-center py-8">
          <div className="text-red-500">{error}</div>
        </div>
      )}

      {/* Products List */}
      {!loading && !error && (
        <div className="flex-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 320px)' }}>
          {filteredProducts.map(product => {
            const isSelected = !!selectedProducts[product.id];
            const quantity = selectedProducts[product.id]?.quantity || 0;

            return (
              <div key={product.id} className="px-4 py-3 border-b border-gray-border">
                <div className="flex items-center gap-3">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleProductToggle(product.id)}
                    className="w-5 h-5 text-purple-primary border-gray-border rounded focus:ring-purple-primary"
                  />

                  {/* Product Image */}
                  <div className="relative w-[60px] h-[60px] flex-shrink-0">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover rounded"
                    />
                  </div>

                  {/* Product Info */}
                  <div className="flex-1">
                    <h3 className="text-[16px] font-['Open_Sans'] font-normal text-black">{product.name}</h3>
                    <p className="text-[14px] font-['Open_Sans'] text-purple-primary">{product.price.toLocaleString()} ₸</p>
                  </div>

                  {/* Quantity Controls */}
                  {isSelected && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuantityChange(product.id, -1);
                        }}
                        className="w-8 h-8 bg-gray-input rounded flex items-center justify-center"
                      >
                        <span className="text-lg leading-none">−</span>
                      </button>
                      <span className="text-[16px] font-['Open_Sans'] min-w-[20px] text-center">{quantity}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuantityChange(product.id, 1);
                        }}
                        className="w-8 h-8 bg-purple-primary rounded flex items-center justify-center"
                      >
                        <span className="text-white text-lg leading-none">+</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Bottom Bar with Total and Next Button */}
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-border">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[18px] font-['Open_Sans'] font-normal">Итого:</span>
            <span className="text-[20px] font-['Open_Sans'] font-bold text-purple-primary">
              {total.toLocaleString()} ₸
            </span>
          </div>
          <button
            onClick={handleNext}
            disabled={Object.keys(selectedProducts).length === 0}
            className={`w-full py-3 rounded-lg text-white text-[16px] font-['Open_Sans'] font-semibold ${
              Object.keys(selectedProducts).length > 0
                ? 'bg-purple-primary'
                : 'bg-gray-disabled opacity-50 cursor-not-allowed'
            }`}
          >
            Далее
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateOrder;