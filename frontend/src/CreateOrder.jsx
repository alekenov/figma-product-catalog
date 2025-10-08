import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchInput from './components/SearchInput';
import DateTimeSelectorAdmin from './components/DateTimeSelectorAdmin';
import { productsAPI, formatProductForDisplay } from './services/api';
import './App.css';

const CreateOrder = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const searchInputRef = useRef(null);

  // Delivery time state
  const [deliveryMode, setDeliveryMode] = useState('asap'); // 'asap' or 'scheduled'
  const [deliveryDate, setDeliveryDate] = useState('');
  const [deliveryTime, setDeliveryTime] = useState('');
  const [confirmTimeWithRecipient, setConfirmTimeWithRecipient] = useState(false);

  // New UI state for date/time selector
  const [selectedDate, setSelectedDate] = useState('tomorrow'); // 'today' | 'tomorrow'
  const [selectedTime, setSelectedTime] = useState('15:00-17:00'); // '09:00-11:00' etc.

  // Get nearest delivery slot (example: 2 hours from now)
  const getNearestSlot = () => {
    const now = new Date();
    now.setHours(now.getHours() + 2);
    const hours = now.getHours();
    const startHour = hours < 10 ? `0${hours}` : hours;
    const endHour = hours + 2 < 10 ? `0${hours + 2}` : hours + 2;
    return `${startHour}:00-${endHour}:00`;
  };

  // Get tomorrow's date in YYYY-MM-DD format
  const getTomorrowDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

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

        // Set default delivery date to tomorrow
        setDeliveryDate(getTomorrowDate());
        setDeliveryTime('15:00-17:00');
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

  // Handle product selection (toggle with default quantity 1)
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

    // Convert selectedDate ('today'/'tomorrow') to YYYY-MM-DD format
    const getDateFromSelection = () => {
      const targetDate = new Date();
      if (selectedDate === 'tomorrow') {
        targetDate.setDate(targetDate.getDate() + 1);
      }
      return targetDate.toISOString().split('T')[0];
    };

    // Prepare delivery data
    const deliveryData = {
      mode: deliveryMode,
      date: deliveryMode === 'asap' ? new Date().toISOString().split('T')[0] : getDateFromSelection(),
      time: deliveryMode === 'asap' ? getNearestSlot() : selectedTime,
      confirmTimeWithRecipient
    };

    // Pass selected products and delivery info to next step
    navigate('/create-order/customer', {
      state: { selectedProducts, total, delivery: deliveryData }
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

      {/* Step indicator (2 steps now) */}
      <div className="px-4 mb-4">
        <div className="flex items-center justify-between max-w-[200px]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-primary rounded-full flex items-center justify-center text-white text-[14px] font-bold">1</div>
            <span className="text-[14px] font-['Open_Sans'] text-black">Товары</span>
          </div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 bg-gray-neutral rounded-full flex items-center justify-center text-gray-disabled text-[14px] font-bold">2</div>
            <span className="text-[14px] font-['Open_Sans'] text-gray-disabled">Клиент</span>
          </div>
        </div>
      </div>

      {/* Search - Always visible for product selection */}
      <SearchInput
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        placeholder="Поиск товаров..."
        inputRef={searchInputRef}
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
        <div className="flex-1 overflow-y-auto pb-[450px]">
          <div className="px-4 space-y-2">
            {filteredProducts.map(product => {
              const isSelected = !!selectedProducts[product.id];
              const quantity = selectedProducts[product.id]?.quantity || 0;

              return (
                <div
                  key={product.id}
                  className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer ${
                    isSelected ? 'border-purple-primary bg-purple-primary bg-opacity-5' : 'border-gray-border'
                  }`}
                  onClick={() => handleProductToggle(product.id)}
                >
                  {/* Product Image - Small */}
                  <div className="relative w-16 h-16 flex-shrink-0">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover rounded"
                    />
                    {isSelected && (
                      <div className="absolute -top-1 -right-1 w-5 h-5 bg-purple-primary rounded-full flex items-center justify-center">
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                          <path d="M13 4L6 11L3 8" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-[14px] font-['Open_Sans'] font-normal text-black line-clamp-2 mb-1">
                      {product.name}
                    </h3>
                    <p className="text-[14px] font-['Open_Sans'] font-bold text-purple-primary">
                      {product.price.toLocaleString()} ₸
                    </p>
                  </div>

                  {/* Quantity Controls */}
                  {isSelected && (
                    <div className="flex items-center gap-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuantityChange(product.id, -1);
                        }}
                        className="w-7 h-7 bg-gray-input rounded flex items-center justify-center"
                      >
                        <span className="text-sm leading-none">−</span>
                      </button>
                      <span className="text-[16px] font-['Open_Sans'] font-bold min-w-[20px] text-center">{quantity}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleQuantityChange(product.id, 1);
                        }}
                        className="w-7 h-7 bg-purple-primary rounded flex items-center justify-center"
                      >
                        <span className="text-white text-sm leading-none">+</span>
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Delivery Time Section - Fixed at bottom */}
      {!loading && !error && (
        <div className="fixed bottom-[130px] left-0 right-0 bg-white border-t border-gray-border pt-4 pb-4" style={{ maxWidth: '320px', margin: '0 auto' }}>
          <div className="px-4">
            <h2 className="text-[18px] font-['Open_Sans'] font-semibold mb-4">Когда доставить?</h2>

            {/* Delivery Mode Toggle */}
            <div className="space-y-3 mb-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="radio"
                  name="deliveryMode"
                  value="asap"
                  checked={deliveryMode === 'asap'}
                  onChange={(e) => setDeliveryMode(e.target.value)}
                  className="w-5 h-5 text-purple-primary border-gray-border focus:ring-purple-primary"
                />
                <div className="flex-1">
                  <div className="text-[16px] font-['Open_Sans'] font-semibold">🚀 Как можно скорее</div>
                  <div className="text-[14px] font-['Open_Sans'] text-gray-placeholder">
                    Сегодня, {getNearestSlot()}
                  </div>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="radio"
                  name="deliveryMode"
                  value="scheduled"
                  checked={deliveryMode === 'scheduled'}
                  onChange={(e) => setDeliveryMode(e.target.value)}
                  className="w-5 h-5 text-purple-primary border-gray-border focus:ring-purple-primary"
                />
                <div className="text-[16px] font-['Open_Sans'] font-semibold">📅 Выбрать время</div>
              </label>
            </div>

            {/* Scheduled Time Inputs */}
            {deliveryMode === 'scheduled' && (
              <div className="space-y-3 pl-8">
                <DateTimeSelectorAdmin
                  selectedDate={selectedDate}
                  onDateChange={setSelectedDate}
                  selectedTime={selectedTime}
                  onTimeChange={setSelectedTime}
                />

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={confirmTimeWithRecipient}
                    onChange={(e) => setConfirmTimeWithRecipient(e.target.checked)}
                    className="w-5 h-5 text-purple-primary border-gray-border rounded focus:ring-purple-primary"
                  />
                  <span className="text-[14px] font-['Open_Sans']">Уточнить время у получателя</span>
                </label>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Bottom Bar with Total and Next Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-border" style={{ maxWidth: '320px', margin: '0 auto' }}>
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
