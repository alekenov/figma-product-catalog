import React, { useState, useRef, useEffect } from 'react';

/**
 * Кастомный селектор ингредиентов с поиском и карточками
 * Заменяет стандартный select для улучшенного UX
 */
const IngredientSelector = ({
  warehouseItems,
  selectedItemId,
  onSelect,
  placeholder = "Начните вводить название..."
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Найти выбранный элемент
  const selectedItem = warehouseItems.find(item => item.id === parseInt(selectedItemId));

  // Фильтрация по поисковому запросу
  const filteredItems = warehouseItems.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Закрытие dropdown при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    onSelect(item.id);
    setIsOpen(false);
    setSearchQuery('');
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  return (
    <div ref={wrapperRef} className="relative">
      {/* Input для поиска */}
      <div className="relative">
        <input
          type="text"
          className="w-full pb-2 border-b border-gray-border text-base font-['Open_Sans'] placeholder-gray-disabled outline-none"
          placeholder={selectedItem ? selectedItem.name : placeholder}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={handleInputFocus}
        />

        {/* Иконка поиска или выбранного элемента */}
        <div className="absolute right-0 top-0 flex items-center h-full">
          {selectedItem ? (
            <svg className="w-5 h-5 text-green-success" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
            </svg>
          ) : (
            <svg className="w-5 h-5 text-gray-placeholder" viewBox="0 0 20 20" fill="none">
              <path d="M8.5 3C5.46243 3 3 5.46243 3 8.5C3 11.5376 5.46243 14 8.5 14C9.83879 14 11.0659 13.5217 12.0196 12.7266L15.6464 16.3536C15.8417 16.5488 16.1583 16.5488 16.3536 16.3536C16.5488 16.1583 16.5488 15.8417 16.3536 15.6464L12.7266 12.0196C13.5217 11.0659 14 9.83879 14 8.5C14 5.46243 11.5376 3 8.5 3Z" fill="currentColor"/>
            </svg>
          )}
        </div>
      </div>

      {/* Dropdown с результатами поиска */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-border rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {filteredItems.length > 0 ? (
            filteredItems.map(item => (
              <div
                key={item.id}
                onClick={() => handleSelect(item)}
                className={`p-3 cursor-pointer hover:bg-gray-input transition-colors border-b border-gray-border last:border-0 ${
                  selectedItemId === item.id ? 'bg-gray-input-alt' : ''
                }`}
              >
                <div className="font-['Open_Sans'] font-semibold text-base mb-1 break-words">
                  {item.name}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-disabled">Цена:</span>
                  <span className="font-semibold text-black">
                    {Math.floor(item.cost_price / 100).toLocaleString()} ₸/шт
                  </span>
                  {item.quantity < 10 && (
                    <span className="text-red-500 text-xs ml-auto">⚠️ мало на складе</span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-gray-disabled">
              Ничего не найдено
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IngredientSelector;
